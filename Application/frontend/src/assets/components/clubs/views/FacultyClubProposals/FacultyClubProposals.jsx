import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/mockbackendApis/clubsApis/clubs';
import styles from './FacultyClubProposals.module.css';
import { useSession } from '../../../../../context/SessionContext';
import { dashboardIcons } from '../../../../icons/registry';

const FacultyClubProposals = () => {
  const { user } = useSession();
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProposals();
  }, [user]);

  const fetchProposals = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const allProposals = await clubsApi.getClubProposals();
      // Filter proposals where this faculty member is the advisor
      const myProposals = allProposals.filter(p => p.facultyAdvisorEmail === user.email);
      setProposals(myProposals);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRecommend = async (proposalId) => {
    try {
      await clubsApi.recommendClubProposal(proposalId, user.id);
      fetchProposals();
    } catch (err) {
      alert("Failed to recommend proposal");
    }
  };

  const handleReject = async (proposalId) => {
    if (!window.confirm("Reject this proposal?")) return;
    try {
      await clubsApi.rejectClubProposal(proposalId, user.id);
      fetchProposals();
    } catch (err) {
      alert("Failed to reject proposal");
    }
  };

  if (loading) return <div className={styles.loading}>Loading proposals...</div>;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h2>Club Proposals</h2>
          <p>Review student proposals requesting you as Faculty Advisor</p>
        </div>
      </header>

      {proposals.length === 0 ? (
        <div className={styles.emptyState}>
          <Icon icon={dashboardIcons.fileDocumentOutline} className={styles.emptyIcon} />
          <p>You have no pending club proposals to review.</p>
        </div>
      ) : (
        <div className={styles.proposalsList}>
          {proposals.map(proposal => (
            <div key={proposal.id} className={styles.proposalCard}>
              <div className={styles.cardHeader}>
                <h3>{proposal.proposed_name}</h3>
                <span className={`${styles.statusBadge} ${styles[proposal.status]}`}>
                  {proposal.status.toUpperCase()}
                </span>
              </div>
              <div className={styles.cardBody}>
                <p><strong>Category:</strong> {proposal.proposed_category}</p>
                <p><strong>Proposed by:</strong> {proposal.proposer?.full_name || 'Unknown'}</p>
                <p className={styles.desc}>{proposal.proposal_description}</p>
              </div>
              
              {proposal.status === 'submitted' && (
                <div className={styles.actions}>
                  <button className={styles.rejectBtn} onClick={() => handleReject(proposal.id)}>
                    Decline
                  </button>
                  <button className={styles.recommendBtn} onClick={() => handleRecommend(proposal.id)}>
                    Recommend & Approve
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FacultyClubProposals;
