import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, info: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary caught an error", error, info);
    this.setState({ info });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', background: '#fee', color: '#c00', borderRadius: '8px', zIndex: 99999, position: 'fixed', top: '10%', left: '10%', right: '10%', maxHeight: '80vh', overflow: 'auto' }}>
          <h2>UI Render Error (Profile Modal)</h2>
          <pre style={{ whiteSpace: 'pre-wrap', fontWeight: 'bold' }}>{this.state.error && this.state.error.toString()}</pre>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>{this.state.info?.componentStack}</pre>
          <button onClick={() => this.props.onClose && this.props.onClose()} style={{ marginTop: '1rem', padding: '0.5rem 1rem' }}>Close Modal</button>
        </div>
      );
    }
    return this.props.children;
  }
}
