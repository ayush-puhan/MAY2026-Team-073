import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { DataTable, RowChevron } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { FilterTabs } from '../../ui/FilterTabs/FilterTabs';
import { universityAdminApi } from '@api/universityAdminApis/universityAdmin';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { ApprovalDecisionModal } from './ApprovalDecisionModal/ApprovalDecisionModal';
import styles from './ClubApprovalQueue.module.css';

export const ClubApprovalQueue = () => {
  const { user } = useSession();
  const { showSuccess, showError } = useToast();
  const [requests, setRequests] = useState([]);
  const [pendingActivations, setPendingActivations] = useState([]);
  const [facultyOptions, setFacultyOptions] = useState([]);
  const [activeTab, setActiveTab] = useState('submitted');
  const [loading, setLoading] = useState(true);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [selectedActivationClub, setSelectedActivationClub] = useState(null);

  const load = async () => {
    setLoading(true);
    const [reqs, activations, faculty] = await Promise.all([
      universityAdminApi.getClubCreationRequests(),
      universityAdminApi.getPendingClubActivations(),
      universityAdminApi.getFacultyAdvisors(),
    ]);
    setRequests(reqs);
    setPendingActivations(activations);
    setFacultyOptions(faculty);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const filtered = requests.filter((r) => r.status === activeTab);
  const tabs = [
    { id: 'submitted', label: 'Pending', count: requests.filter((r) => r.status === 'submitted').length },
    { id: 'approved', label: 'Approved', count: requests.filter((r) => r.status === 'approved').length },
    { id: 'rejected', label: 'Rejected', count: requests.filter((r) => r.status === 'rejected').length },
  ];

  const handleDecide = async (status, { comments, facultyAdvisorId }) => {
    try {
      await universityAdminApi.decideClubCreationRequest(selectedRequest.id, {
        status,
        reviewed_by: user.id,
        review_comments: comments,
        faculty_advisor_id: facultyAdvisorId,
      });
      showSuccess(`Club proposal ${status}.`);
      setSelectedRequest(null);
      load();
    } catch (err) {
      showError(err.message || 'Failed to update proposal.');
    }
  };

  const handleActivate = async (status, { facultyAdvisorId }) => {
    try {
      await universityAdminApi.activateClub(selectedActivationClub.id, facultyAdvisorId);
      showSuccess('Club activated.');
      setSelectedActivationClub(null);
      load();
    } catch (err) {
      showError(err.message || 'Failed to activate club.');
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <Icon icon="mdi:loading" className="animate-spin" width="32" />
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Club Approvals</h2>
        <p className={styles.subtitle}>Review new club proposals and assign faculty advisors.</p>
      </div>

      {pendingActivations.length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Awaiting Advisor Assignment</h3>
          <DataTable
            columns={[
              { header: 'Club', accessor: 'name' },
              { header: 'Category', accessor: 'category' },
              { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
              { header: '', cell: () => <RowChevron /> },
            ]}
            data={pendingActivations}
            onRowClick={(row) => setSelectedActivationClub(row)}
          />
        </div>
      )}

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Proposal History</h3>
        <FilterTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
        <DataTable
          columns={[
            { header: 'Proposed Club', accessor: 'proposed_name' },
            { header: 'Category', accessor: 'proposed_category' },
            { header: 'Requested By', accessor: 'requested_by_name' },
            { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
            { header: '', cell: (row) => row.status === 'submitted' ? <RowChevron /> : null },
          ]}
          data={filtered}
          onRowClick={(row) => setSelectedRequest(row)}
          isRowClickable={(row) => row.status === 'submitted'}
          emptyIcon="mdi:check-decagram-outline"
          emptyTitle={`No ${activeTab} proposals`}
          emptyDesc={`There are currently no ${activeTab} club creation requests.`}
        />
      </div>

      {selectedRequest && (
        <ApprovalDecisionModal
          mode="request"
          title={selectedRequest.proposed_name}
          subtitle={selectedRequest.proposal_description}
          facultyOptions={facultyOptions}
          onClose={() => setSelectedRequest(null)}
          onDecide={handleDecide}
        />
      )}

      {selectedActivationClub && (
        <ApprovalDecisionModal
          mode="activation"
          title={selectedActivationClub.name}
          subtitle="This club was approved but still needs a faculty advisor before it can go active."
          facultyOptions={facultyOptions}
          onClose={() => setSelectedActivationClub(null)}
          onDecide={handleActivate}
        />
      )}
    </div>
  );
};
