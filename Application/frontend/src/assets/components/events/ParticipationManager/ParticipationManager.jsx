import React, { useEffect, useState } from 'react';
import { Icon } from '@iconify/react';

import { api } from '../../../../api/api';
import { EmptyState } from '../../ui/EmptyState/EmptyState';

import styles from '../AttendanceManager/AttendanceManager.module.css';

const ParticipationManager = ({
  eventId,
  onClose
}) => {
  const [registrations, setRegistrations] = useState([]);
  const [externalParticipants, setExternalParticipants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchParticipation();
  }, [eventId]);

  const fetchParticipation = async () => {
    try {
      setLoading(true);

      const [
        registrationsResponse,
        externalResponse,
        usersResponse
      ] = await Promise.all([
        api.get(
          `/event_registrations?event_id=${eventId}`
        ),
        api.get(
          `/external_participants?event_id=${eventId}`
        ),
        api.get('/users')
      ]);

      const registrations = Array.isArray(
        registrationsResponse
      )
        ? registrationsResponse
        : [];

      const externalParticipants = Array.isArray(
        externalResponse
      )
        ? externalResponse
        : [];

      const users = Array.isArray(usersResponse)
        ? usersResponse
        : [];

      /*
       * Create user lookup.
       */
      const userMap = users.reduce(
        (acc, user) => {
          acc[user.id] = user;
          return acc;
        },
        {}
      );

      /*
       * Attach user information to
       * internal registrations.
       */
      const internal = registrations.map(
        registration => ({
          ...registration,
          user: userMap[registration.user_id]
        })
      );

      setRegistrations(internal);
      setExternalParticipants(
        externalParticipants
      );

    } catch (error) {
      console.error(
        'Failed to load participation data:',
        error
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '2rem' }}>
        Loading participation data...
      </div>
    );
  }

  const totalParticipants =
    registrations.length +
    externalParticipants.length;

  return (
    <div className={styles.container}>

      <div className={styles.header}>

        <div>
          <h3>
            Registrations & Participation
          </h3>

          <div className={styles.stats}>
            {totalParticipants} Total Participants
          </div>
        </div>

        <button
          className={styles.closeBtn}
          onClick={onClose}
          aria-label="Close"
        >
          <Icon icon="mdi:close" />
        </button>

      </div>

      {totalParticipants === 0 ? (

        <EmptyState
          icon="mdi:account-group-outline"
          title="No participants yet"
          description="There are no registrations or external participants for this event."
        />

      ) : (

        <div className={styles.rosterList}>

          {/* INTERNAL REGISTRATIONS */}

          {registrations.map(
            registration => {

              const user =
                registration.user;

              return (
                <div
                  key={`registration-${registration.id}`}
                  className={styles.rosterItem}
                >

                  <div className={styles.userInfo}>

                    <div className={styles.avatar}>

                      {user?.avatar ? (

                        <img
                          src={user.avatar}
                          alt={user.full_name}
                        />

                      ) : (

                        user?.full_name
                          ?.charAt(0)
                          ?.toUpperCase() || '?'

                      )}

                    </div>

                    <div
                      className={
                        styles.userDetails
                      }
                    >

                      <span
                        className={
                          styles.userName
                        }
                      >
                        {user?.full_name ||
                          `User #${registration.user_id}`}
                      </span>

                      <span
                        className={
                          styles.userEmail
                        }
                      >
                        {user?.email ||
                          'Email unavailable'}
                      </span>

                    </div>

                  </div>

                  <div
                    className={
                      styles.actionArea
                    }
                  >

                    <span>
                      {registration.status ||
                        'registered'}
                    </span>

                  </div>

                </div>
              );
            }
          )}

          {/* EXTERNAL PARTICIPANTS */}

          {externalParticipants.map(
            participant => {

              return (
                <div
                  key={`external-${participant.id}`}
                  className={styles.rosterItem}
                >

                  <div className={styles.userInfo}>

                    <div
                      className={styles.avatar}
                    >
                      {participant.full_name
                        ?.charAt(0)
                        ?.toUpperCase() || '?'}
                    </div>

                    <div
                      className={
                        styles.userDetails
                      }
                    >

                      <span
                        className={
                          styles.userName
                        }
                      >
                        {participant.full_name}
                        {' (External)'}
                      </span>

                      <span
                        className={
                          styles.userEmail
                        }
                      >
                        {participant.email ||
                          'Email unavailable'}
                      </span>

                    </div>

                  </div>

                  <div
                    className={
                      styles.actionArea
                    }
                  >

                    <span>
                      {participant.participant_type ||
                        'External Participant'}
                    </span>

                  </div>

                </div>
              );
            }
          )}

        </div>
      )}

    </div>
  );
};

export default ParticipationManager;