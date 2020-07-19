import filecmp
import json
import sys
import unittest
import requests_mock
import jiratimereport
from issue import Issue
from worklog import WorkLog
from datetime import datetime


class MyTestCase(unittest.TestCase):

    def test_get_updated_issues_without_parent(self):
        """
        Test when issues do not have a parent issue
        """
        with open("issues_without_parent.json", "r") as issues_file:
            mock_response = issues_file.read()

        with requests_mock.Mocker() as m:
            m.register_uri('GET', '/rest/api/2/search', text=mock_response)
            issues = jiratimereport.get_updated_issues("https://jira_url", "user_name", "api_token", "MYB",
                                                       "2020-01-10", "2020-01-20", "")

        issues_expected_result = [
            Issue(10005, "MYB-5", "Summary of issue MYB-5", None, None, 3600, 900)]

        self.assertListEqual(issues_expected_result, issues, "Issues lists are unequal")

    def test_convert_json_to_issues(self):
        """
        Test the conversion of json issues to object issues
        """
        with open("convert_json_to_issues.json", "r") as issues_file:
            response_json = json.loads(issues_file.read())

        issues = jiratimereport.convert_json_to_issues(response_json)

        issues_expected_result = [
            Issue(10005, "MYB-5", "Summary of issue MYB-5", "MYB-3", "Summary of the parent issue of MYB-5", 3600, 900),
            Issue(10004, "MYB-4", "Summary of issue MYB-4", "MYB-3", "Summary of the parent issue of MYB-4", None, None)]

        self.assertListEqual(issues_expected_result, issues, "Issues lists are unequal")

    def test_get_updated_issues_one_page(self):
        """
        Test the single page response when retrieving Jira issues
        """
        with open("issues_one_page.json", "r") as issues_file:
            mock_response = issues_file.read()

        with requests_mock.Mocker() as m:
            m.register_uri('GET', '/rest/api/2/search', text=mock_response)
            issues = jiratimereport.get_updated_issues("https://jira_url", "user_name", "api_token", "MYB",
                                                       "2020-01-10", "2020-01-20", "")

        issues_expected_result = [
            Issue(10005, "MYB-5", "Summary of issue MYB-5", "MYB-3", "Summary of the parent issue of MYB-5", 3600, 900),
            Issue(10004, "MYB-4", "Summary of issue MYB-4", "MYB-3", "Summary of the parent issue of MYB-4", 7200, 600)]

        self.assertListEqual(issues_expected_result, issues, "Issues lists are unequal")

    def test_get_updated_issues_multiple_pages(self):
        """
        Test the multiple pages response when retrieving Jira issues (pagination)
        """
        with open("issues_multiple_first_page.json", "r") as issues_first_file:
            mock_response_first_page = issues_first_file.read()

        with open("issues_multiple_second_page.json", "r") as issues_second_file:
            mock_response_second_page = issues_second_file.read()

        with requests_mock.Mocker() as m:
            m.register_uri('GET', '/rest/api/2/search', [{'text': mock_response_first_page},
                                                         {'text': mock_response_second_page}])
            issues = jiratimereport.get_updated_issues("https://jira_url", "user_name", "api_token", "MYB",
                                                       "2020-01-10", "2020-01-20", "")

        issues_expected_result = [
            Issue(10005, "MYB-5", "Summary of issue MYB-5", "MYB-3", "Summary of the parent issue of MYB-5", 3600, 900),
            Issue(10004, "MYB-4", "Summary of issue MYB-4", "MYB-3", "Summary of the parent issue of MYB-4", 7200, 600),
            Issue(10006, "MYB-6", "Summary of issue MYB-6", "MYB-3", "Summary of the parent issue of MYB-6", 3600, 900)]

        self.assertListEqual(issues_expected_result, issues, "Issues lists are unequal")

    def test_get_changelogs_one_page(self):
        """
        Test the single page response when retrieving Jira changelogs
        """
        with open("changelogs_first_issue_one_page.json", "r") as first_issue_file:
            mock_response_first_issue = first_issue_file.read()

        with open("changelogs_second_issue_one_page.json", "r") as second_issue_file:
            mock_response_second_issue = second_issue_file.read()

        issues = [Issue(10005, "MYB-5", "Summary of issue MYB-5", "MYB-3", "Summary of the parent issue of MYB-5", 3600, 900),
                  Issue(10004, "MYB-4", "Summary of issue MYB-4", "MYB-3", "Summary of the parent issue of MYB-4", 7200, 600)]

        with requests_mock.Mocker() as m:
            m.register_uri('GET', '/rest/api/2/issue/MYB-5/changelog/', text=mock_response_first_issue)
            m.register_uri('GET', '/rest/api/2/issue/MYB-4/changelog/', text=mock_response_second_issue)
            jiratimereport.get_issue_time_information("https://jira_url", "user_name", "api_token", "", issues)

        # First start date is a work log
        issue_myb_5 = Issue(10005, "MYB-5", "Summary of issue MYB-5", "MYB-3", "Summary of the parent issue of MYB-5", 3600, 900)
        issue_myb_5.set_issue_start_date(datetime(2020, 1, 10))
        # First start date is based on status
        issue_myb_4 = Issue(10004, "MYB-4", "Summary of issue MYB-4", "MYB-3", "Summary of the parent issue of MYB-4", 7200, 600)
        issue_myb_4.set_issue_start_date(datetime(2020, 1, 12))
        issue_myb_4.set_issue_end_date(datetime(2020, 1, 15))

        issues_expected_result = [issue_myb_5,
                                  issue_myb_4]

        self.assertListEqual(issues_expected_result, issues, "Issue lists are unequal")

    def test_get_work_logs_one_page(self):
        """
        Test the single page response when retrieving Jira work logs
        """
        with open("work_logs_first_issue_one_page.json", "r") as first_issue_file:
            mock_response_first_issue = first_issue_file.read()

        with open("work_logs_second_issue_one_page.json", "r") as second_issue_file:
            mock_response_second_issue = second_issue_file.read()

        issues = [Issue(10005, "MYB-5", "Summary of issue MYB-5", "MYB-3", "Summary of the parent issue of MYB-5", 3600, 900),
                  Issue(10004, "MYB-4", "Summary of issue MYB-4", "MYB-3", "Summary of the parent issue of MYB-4", 7200, 600)]

        with requests_mock.Mocker() as m:
            m.register_uri('GET', '/rest/api/2/issue/MYB-5/worklog/', text=mock_response_first_issue)
            m.register_uri('GET', '/rest/api/2/issue/MYB-4/worklog/', text=mock_response_second_issue)
            work_logs = jiratimereport.get_work_logs("https://jira_url", "user_name", "api_token",
                                                     "2020-01-10", "2020-01-20", "", issues)

        work_logs_expected_result = [WorkLog("MYB-5", datetime(2020, 1, 18), 3600, "John Doe"),
                                     WorkLog("MYB-5", datetime(2020, 1, 18), 5400, "John Doe"),
                                     WorkLog("MYB-4", datetime(2020, 1, 12), 3600, "John Doe")]

        self.assertListEqual(work_logs_expected_result, work_logs, "Work Log lists are unequal")

    def test_get_work_logs_multiple_pages(self):
        """
        Test the multiple pages response when retrieving Jira issues (pagination)
        """
        with open("work_logs_multiple_first_page.json", "r") as issues_first_file:
            mock_response_first_page = issues_first_file.read()

        with open("work_logs_multiple_second_page.json", "r") as issues_second_file:
            mock_response_second_page = issues_second_file.read()

        issues = [Issue(10005, "MYB-5", "Summary of issue MYB-5", "MYB-3", "Summary of the parent issue of MYB-5", 3600, 900)]

        with requests_mock.Mocker() as m:
            m.register_uri('GET', '/rest/api/2/issue/MYB-5/worklog/', [{'text': mock_response_first_page},
                                                                       {'text': mock_response_second_page}])
            work_logs = jiratimereport.get_work_logs("https://jira_url", "user_name", "api_token",
                                                     "2020-01-10", "2020-01-20", "", issues)

        work_logs_expected_result = [WorkLog("MYB-5", datetime(2020, 1, 18), 3600, "John Doe"),
                                     WorkLog("MYB-5", datetime(2020, 1, 18), 5400, "John Doe"),
                                     WorkLog("MYB-5", datetime(2020, 1, 12), 3600, "John Doe")]

        self.assertListEqual(work_logs_expected_result, work_logs, "Work Log lists are unequal")

    def test_output(self):
        """
        Test the different outputs including UTF-16 characters and issue without parent issue
        """
        work_logs = [WorkLog("MYB-7", datetime(2020, 1, 20), 3600, "René Doe"),
                     WorkLog("MYB-5", datetime(2020, 1, 18), 3600, "John Doe"),
                     WorkLog("MYB-5", datetime(2020, 1, 18), 5400, "John Doe"),
                     WorkLog("MYB-5", datetime(2020, 1, 12), 3600, "John Doe")]

        issues = [Issue(10005, "MYB-5", "Summary of issue MYB-5", "MYB-3", "Summary of the parent issue of MYB-5", 3600, 900),
                  Issue(10007, "MYB-7", "Summary of issue MYB-7", None, None, None, None)]

        stdout = sys.stdout
        with open('jira-time-report-console.txt', 'w') as sys.stdout:
            jiratimereport.process_work_logs("console", issues, work_logs)
        sys.stdout = stdout
        self.assertTrue(filecmp.cmp('console_output.txt', 'jira-time-report-console.txt'))

        jiratimereport.process_work_logs("csv", issues, work_logs)
        self.assertTrue(filecmp.cmp('csv_output.csv', 'jira-time-report.csv'))

        jiratimereport.process_work_logs("excel", issues, work_logs)
        self.assertTrue(filecmp.cmp('excel_output.xlsx', 'excel_output.xlsx'))


if __name__ == '__main__':
    unittest.main()
