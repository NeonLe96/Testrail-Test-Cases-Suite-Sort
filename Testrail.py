#TEST CASE SORT AUTOMATION
#Neon


import testrail
import subprocess
import ssl
import argparse

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

#Credentials to access y Testrail
tr_client = testrail.APIClient('')
tr_client.user = ''
tr_client.password = ''
    

parser = argparse.ArgumentParser()
parser.add_argument("-a","--add", help="add any test cases in the General Regression test run or test plan from a MILESTONE into the Partial Regression suite", type = int, metavar='')
parser.add_argument("-c", "--check", help= "Display info about a test PLAN", type= int , metavar='')
parser.add_argument("--remove", help= "Remove ALL test cases in x from Partial regression as well as setting non-automation-status test cases to ToBeAutomated",action="store_true")
args = parser.parse_args()

if args.add:
    Milestone = args.add
    milestone_runs = tr_client.send_get('get_runs/1&milestone_id=%s'%Milestone)
    plans = tr_client.send_get('get_plans/1&milestone_id=%s'%Milestone) #Milestone ID is here
    for plan in plans :
        if "General Regression" in plan['name']:
            plan_id = plan['id']
            runs = tr_client.send_get('get_plan/%s'%plan_id)
            for run in runs['entries']:
                run_id = run['runs'][0]['id'] #second value is always 0  
                run_tests = tr_client.send_get('get_tests/%s'%run_id)
                #loop here with the number of test in the Run
                for run_test in run_tests:
                    test_case_id = run_test['case_id']
                    case_info = tr_client.send_get('get_case/%s'%test_case_id)
                    #If statement, if custom_testsuite existed, check if it has 3 which is partial regression, if it has 3 ignore, if it doesn't add 3.
                    #if it doesn't have custom_testsuite, add custom_testsuite with value as 3
                    initial_case_info_add_partial = case_info
                    add_custompartial= case_info
                    if 'custom_testsuite' in case_info:
                        if 3 in case_info['custom_testsuite']:
                            print "Test %s is already in Partial Regression Suite"%test_case_id
                            pass
                        elif 3 not in case_info['custom_testsuite']:
                            print "Test %s is not in Partial Regression Suite and has been added" %test_case_id
                            initial_case_info_add_partial['custom_testsuite'].append(3)
                            tr_client.send_post('update_case/%s'%test_case_id,initial_case_info_add_partial)
                    else:
                        add_custompartial['custom_testsuite'] = [3]
                        tr_client.send_post('update_case/%s'%test_case_id,add_custompartial)
                        print "Test %s is not in Partial Regression Suite and has been added"%test_case_id
        else:
            print "This plan is not General"
    
    for milestone_run in milestone_runs:
        if "General Regression" in milestone_run['name']:
            milestone_run_id = milestone_run['id'] #Getting the Run ID
            milestone_run_tests = tr_client.send_get('get_tests/%s'%milestone_run_id) #Return LIST of info of all Test
            for milestone_run_test in milestone_run_tests:
                run_case_id = milestone_run_test['case_id']
                case_info = tr_client.send_get('get_case/%s'%run_case_id)
                #If statement, if custom_testsuite existed, check if it has 3 which is partial regression, if it has 3 ignore, if it doesn't add 3.
                #if it doesn't have custom_testsuite, add custom_testsuite with value as 3
                initial_case_info_add_partial = case_info
                add_custompartial= case_info
                if 'custom_testsuite' in case_info:
                    if 3 in case_info['custom_testsuite']:
                            print "Test %s is already in Partial Regression Suite" %run_case_id
                            pass
                    elif 3 not in case_info['custom_testsuite']:
                            print "Test %s is not in Partial Regression Suite and has been added" %run_case_id
                            initial_case_info_add_partial['custom_testsuite'].append(3)
                            tr_client.send_post('update_case/%s'%run_case_id,initial_case_info_add_partial)
                else:
                    add_custompartial['custom_testsuite'] = [3]
                    tr_client.send_post('update_case/%s'%run_case_id,add_custompartial)
                    print "Test %s is not in Partial Regression Suite and has been added" %run_case_id
        else:
           print " No General Regression Run detected"

if args.check:
    plan_number = args.check #Change this to arg.x
    
    planget = tr_client.send_get('get_plan/%s'%plan_number)
    runs = planget['entries']
    n=0
    test_case_list = []
    for run in runs:
        tests = tr_client.send_get('get_tests/%s' %run['runs'][0]['id'])
        Id = run['runs'][0]['id']
        testgets = tr_client.send_get('get_tests/%s'%Id)
        for testget in testgets:
            test_case_list.append(testget['case_id'])
    test_case_list.sort()
    Sortedlist = sorted(set(test_case_list))
    print test_case_list
    print "The number of test runs in this test plan is: ", len(test_case_list)
    print "The number of unique test cases in this test plan is: ", len(Sortedlist)

if args.remove:
    all_test_cases = tr_client.send_get('get_cases/1')  
    for all_test_case in all_test_cases:
        if 'custom_testsuite' in all_test_case:
            if 3 in all_test_case['custom_testsuite']:
                all_test_case_delete_partial = all_test_case
                if all_test_case_delete_partial['custom_case_automation_status'] == None:
                    all_test_case_delete_partial['custom_case_automation_status'] = 2
                    print "%s set to To Be Automated" %all_test_case_delete_partial['id']
                else:
                    pass
                all_test_case_delete_partial['custom_testsuite'].remove(3)
                tr_client.send_post('update_case/%s'%all_test_case_delete_partial['id'], all_test_case_delete_partial)
                print "%s is not in Partial Regression Anymore" %all_test_case_delete_partial['id']
            else:
                print "%s is in another test suite or not in any test suite at all" %all_test_case['id']
        else:
            all_test_case_add_automationstatus = all_test_case
            if all_test_case_add_automationstatus['custom_case_automation_status'] == None:
                all_test_case_add_automationstatus['custom_case_automation_status'] = 2
                print "%s set to To Be Automated" %all_test_case_add_automationstatus['id']
                tr_client.send_post('update_case/%s'%all_test_case_add_automationstatus['id'], all_test_case_add_automationstatus)
            else:
                pass
