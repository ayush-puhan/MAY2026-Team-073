import React, { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import { Icon } from '@iconify/react';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { aiApi } from '../../../../api';
import { Button } from '../../ui/Button/Button';
import styles from './AIChatbot.module.css';

// ── Quick Action Suggestions ──
const QUICK_ACTIONS = [
  { label: 'Recommend me a club', icon: 'mdi:compass-outline' },
  { label: 'Show my attendance', icon: 'mdi:calendar-check-outline' },
  { label: 'My reward points', icon: 'mdi:star-four-points-outline' },
  { label: 'Upcoming events', icon: 'mdi:calendar-clock-outline' },
  { label: 'My memberships', icon: 'mdi:account-group-outline' },
  { label: 'Help with platform', icon: 'mdi:help-circle-outline' },
];

// ── Unique ID generator ──
let _msgId = 0;
const nextId = () => `msg-${++_msgId}-${Date.now()}`;

export const AIChatbot = () => {
  const { user } = useSession();
  const { addToast } = useToast();

  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const messageEndRef = useRef(null);
  const textareaRef = useRef(null);

  // ── Auto-scroll to bottom on new messages ──
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // ── Auto-resize textarea ──
  const adjustTextarea = useCallback(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`;
    }
  }, []);

  // ── Send message handler ──
  const handleSend = async (overrideMessage) => {
    const text = (overrideMessage || inputValue).trim();
    if (!text || isLoading) return;

    // Add user message
    const userMsg = {
      id: nextId(),
      role: 'user',
      content: text,
    };
    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      const data = await aiApi.chat(text);

      const botMsg = {
        id: nextId(),
        role: 'assistant',
        content: data.response || 'I received your message but couldn\'t generate a response.',
        intent: data.detected_intent || null,
        authorized: data.authorized !== false,
        cacheHit: data.cache_hit || false,
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error('AI Chat error:', err);

      // Check for 503 (ai_unavailable)
      const is503 = err.response?.status === 503;
      const errorMessage = is503
        ? (err.response?.data?.message || 'The AI assistant is temporarily unavailable. Please try again shortly.')
        : 'Something went wrong. Please check your connection and try again.';

      const errorMsg = {
        id: nextId(),
        role: 'error',
        content: errorMessage,
        intent: err.response?.data?.detected_intent || null,
      };
      setMessages(prev => [...prev, errorMsg]);

      if (!is503) {
        addToast({ title: 'Connection Error', message: 'Could not reach the AI assistant.', type: 'error' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  // ── Keyboard handler ──
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // ── Quick chip click ──
  const handleChipClick = (label) => {
    handleSend(label);
  };

  // ── New chat ──
  const handleNewChat = () => {
    setMessages([]);
    setInputValue('');
  };

  // ── Render a single message ──
  const renderMessage = (msg, idx) => {
    if (msg.role === 'user') {
      return (
        <div key={msg.id} className={`${styles.messageRow} ${styles.messageRowUser}`}>
          <div className={styles.userBubble}>
            {msg.content}
          </div>
        </div>
      );
    }

    if (msg.role === 'error') {
      return (
        <React.Fragment key={msg.id}>
          <div className={`${styles.messageRow} ${styles.messageRowBot}`}>
            <div className={`${styles.botBubble} ${styles.errorBubble}`}>
              <div className={styles.botLabel}>
                <Icon icon="mdi:alert-circle-outline" className={styles.botLabelIcon} />
                <span>Error</span>
              </div>
              <div className={styles.botText}>{msg.content}</div>
            </div>
          </div>
          {msg.intent && (
            <div className={styles.intentBadge}>
              <span className={styles.intentPill}>{msg.intent}</span>
            </div>
          )}
        </React.Fragment>
      );
    }

    // Assistant message
    const isRefusal = msg.authorized === false;
    return (
      <React.Fragment key={msg.id}>
        <div className={`${styles.messageRow} ${styles.messageRowBot}`}>
          <div className={`${styles.botBubble} ${isRefusal ? styles.refusalBubble : ''}`}>
            <div className={styles.botLabel}>
              <Icon icon="mdi:creation" className={styles.botLabelIcon} />
              <span>AI</span>
            </div>
            <div className={styles.botText}>
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        </div>
        {(msg.intent || msg.cacheHit) && (
          <div className={styles.intentBadge}>
            {msg.intent && <span className={styles.intentPill}>{msg.intent}</span>}
            {msg.cacheHit && <span className={styles.cachePill}>⚡ cached</span>}
          </div>
        )}
      </React.Fragment>
    );
  };

  const firstName = user?.full_name?.split(' ')[0] || 'there';
  const hasMessages = messages.length > 0;

  return (
    <div className={styles.container}>
      {/* ── Header ── */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.headerIcon}>
            <Icon icon="mdi:creation" />
          </div>
          <span className={styles.headerTitle}>
            ClubConnect <span className={styles.headerTitleAccent}>AI</span>
          </span>
        </div>
        {hasMessages && (
          <Button variant="ghost" size="sm" icon="mdi:chat-plus-outline" onClick={handleNewChat}>
            New Chat
          </Button>
        )}
      </div>

      {/* ── Message Area ── */}
      <div className={styles.messageArea}>
        {!hasMessages ? (
          <div className={styles.welcomeState}>
            <div className={styles.welcomeIcon}>
              <Icon icon="mdi:creation" />
            </div>
            <h2 className={styles.welcomeTitle}>Hi {firstName}! 👋</h2>
            <p className={styles.welcomeSubtitle}>
              I'm your ClubConnect AI Assistant. Ask me about clubs, events,
              attendance, rewards, memberships, and more.
            </p>
          </div>
        ) : (
          <>
            {messages.map(renderMessage)}
            {isLoading && (
              <div className={`${styles.messageRow} ${styles.messageRowBot}`}>
                <div className={styles.typingBubble}>
                  <span className={styles.typingDot} />
                  <span className={styles.typingDot} />
                  <span className={styles.typingDot} />
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messageEndRef} />
      </div>

      {/* ── Bottom: Chips + Input ── */}
      <div className={styles.bottomSection}>
        {/* Quick chips — show when no messages or after conversation */}
        <div className={styles.chipsRow}>
          {QUICK_ACTIONS.map((chip) => (
            <button
              key={chip.label}
              className={styles.chip}
              onClick={() => handleChipClick(chip.label)}
              disabled={isLoading}
            >
              <Icon icon={chip.icon} className={styles.chipIcon} />
              {chip.label}
            </button>
          ))}
        </div>

        {/* Input bar */}
        <div className={styles.inputBar}>
          <textarea
            ref={textareaRef}
            className={styles.chatInput}
            placeholder="Message ClubConnect AI..."
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              adjustTextarea();
            }}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={isLoading}
          />
          <button
            className={styles.sendBtn}
            onClick={() => handleSend()}
            disabled={!inputValue.trim() || isLoading}
            title="Send message"
          >
            <Icon icon="mdi:arrow-up" />
          </button>
        </div>
      </div>
    </div>
  );
};
