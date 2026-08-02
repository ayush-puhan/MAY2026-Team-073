import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/backendApis/clubsApis/clubs';
import styles from './CertificatesView.module.css';
import { useToast } from '../../../../../context/ToastContext';
import { uiIcons, landingIcons, adminIcons } from '../../../../icons/registry';

const CertificatesView = () => {
  const { currentUserId, user, club } = useOutletContext();
  const { addToast } = useToast();
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCertificates();
  }, [currentUserId]);

  const fetchCertificates = async () => {
    try {
      setLoading(true);
      const data = await clubsApi.getUserCertificates(currentUserId);
      setCertificates(data || []);
    } catch (err) {
      console.error(err);
      setError('Failed to load certificates.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (cert) => {
    const content = `CERTIFICATE OF PARTICIPATION\n\n${cert.title || 'Certificate'}\n\nAwarded to: ${user?.first_name || 'Member'} ${user?.last_name || ''}\nClub: ${club?.name || 'Club'}\nDate: ${cert.issued_date || new Date().toLocaleDateString()}\n\nThis certificate acknowledges your contribution and participation.`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(cert.title || 'certificate').replace(/\s+/g, '_')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    addToast({ title: 'Downloaded', message: 'Certificate downloaded successfully!', type: 'success' });
  };

  if (loading) return <div className={styles.loading}>Loading certificates...</div>;
  if (error) return <div className={styles.error}>{error}</div>;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h2>My Certificates</h2>
          <p>View your earned certificates for volunteering and event participation</p>
        </div>
      </header>

      {certificates.length === 0 ? (
        <div className={styles.emptyState}>
          <Icon icon={uiIcons.certificateOutline} className={styles.emptyIcon} />
          <p>You haven't earned any certificates yet.</p>
          <p className={styles.helpText}>Complete volunteer tasks or attend events to earn certificates!</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {certificates.map(cert => (
            <div key={cert.id} className={styles.card}>
              <div className={styles.cardHeader}>
                <Icon icon={landingIcons.certificate} className={styles.certIcon} />
                <span className={styles.date}>{new Date(cert.issued_at).toLocaleDateString()}</span>
              </div>
              <h3 className={styles.title}>{cert.title}</h3>
              <p className={styles.clubName}>{cert.club?.name || 'Club Activity'}</p>
              <button className={styles.downloadBtn} onClick={() => handleDownload(cert)}>
                <Icon icon={adminIcons.download} /> Download PDF
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CertificatesView;
