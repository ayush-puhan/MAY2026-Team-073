## How to run testcases

- Go to -> Application\backend
    - `cd Application`
    - `cd backend`
- Run pytest here
    - `python -m pytest tests`

- Remove Warning ( if any )
    - `python -m pytest tests -p no:warnings`

- To run particuler testcase or file ( for example )
    - `python -m pytest tests\modules\auth\test_login.py -p no:warnings`


## Test folder structure

```text
tests
|   conftest.py
|   readme.md
|   
+---db_factory
|   |   base.py
|   |   factory.py
|   |   
|           
+---fixtures
|   |   auth_fixture.py
|   |   factory_fixture.py
|   |
|           
+---modules
|   +---announcement
|   |   |   test_get_all_ann.py
|   |   |   test_post_ann.py
|   |   |
|   |           
|   +---auth
|   |   |   test_login.py
|   |   |   test_logout.py
|   |   |   test_register.py
|   |   |   test_resendotp.py
|   |   |   test_verifyotp.py
|   |   |   
|   |   
|   |           
|   +---club_leadership
|   |   +---application_routes
|   |   |   |   test_club_leader_get_all_club_application.py
|   |   |   |   test_review_application.py
|   |   |   |   test_student_submit_application.py
|   |   |   |   test_user_get_club_application.py
|   |   |   |   
|   |   |   
|   |   |           
|   |   +---club_budget
|   |   |   |   test_get_club_budget.py
|   |   |   |   test_get_expences.py
|   |   |   |   test_post_budget.py
|   |   |   |   test_post_expences.py
|   |   |   |   test_update_budget.py
|   |   |   |   test_update_expences.py
|   |   |   |   
|   |   |   
|   |   |           
|   |   +---club_creation_request
|   |   |   |   test_admin_approve_club_req.py
|   |   |   |   test_admin_reject_club_req.py
|   |   |   |   test_admin_view_request.py
|   |   |   |   test_create_request_for_new_club.py
|   |   |   |   test_faculty_recomend_club_req.py
|   |   |   |   test_faculty_view_assigned_proposal.py
|   |   |   |   
|   |   |   
|   |   |           
|   |   +---club_resources
|   |   |   |   test_delete_club_resources.py
|   |   |   |   test_get_club_resources.py
|   |   |   |   test_get_committee_resources.py
|   |   |   |   test_post_club_resources.py
|   |   |   |   
|   |   |   
|   |   |           
|   |   +---committee_routes
|   |   |   |   test_create_committees.py
|   |   |   |   test_delete_committee_membership.py
|   |   |   |   test_get_committees.py
|   |   |   |   test_get_committee_member.py
|   |   |   |   test_patch_committee_membership.py
|   |   |   |   test_post_committee_member.py
|   |   |   |   
|   |   |   
|   |   |           
|   |   \---routes
|   |       |   test_get_all_clubs.py
|   |       |   test_get_club_by_id.py
|   |       |   
|   |              
|   +---faculty
|   |   |   test_faculty_decide_event.py
|   |   |   test_faculty_decide_expense.py
|   |   |   test_faculty_get_advised_clubs.py
|   |   |   test_faculty_get_club_by_id.py
|   |   |   test_faculty_get_events.py
|   |   |   test_faculty_get_expense.py
|   |   |   test_faculty_success_stats.py
|   |   |   
|   |            
|   +---system_admin
|   |   |   test_system_admin_analytics.py
|   |   |   test_system_admin_audit_Log.py
|   |   |   test_system_admin_create_auditlog.py
|   |   |   test_system_admin_create_users.py
|   |   |   test_system_admin_delete_user.py
|   |   |   test_system_admin_get_users.py
|   |   |   test_system_admin_get_user_by_id.py
|   |   |   test_system_admin_stats.py
|   |   |   test_system_admin_university_get_post.py
|   |   |   test_system_admin_update_role.py
|   |   |   test_system_admin_update_university_by_id.py
|   |   |   test_system_admin_user_status_update.py
|   |   |   
|   |   
|   |           
|   +---university_admin
|       |   test_ua_activate_club.py
|       |   test_ua_club_request_decision.py
|       |   test_ua_get_all_club.py
|       |   test_ua_get_all_events.py
|       |   test_ua_get_analytics.py
|       |   test_ua_get_club_requests.py
|       |   test_ua_get_faculty.py
|       |   test_ua_get_pending_club_activation.py
|       |   test_ua_get_stats.py
|       |   

        


```
## What implemented 
The test file names indecate what is being added.Test case folder structure resemble the application folder structure.


