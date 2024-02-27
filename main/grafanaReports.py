import requests

def generate_grafana_report(api_url, api_key, dashboard_uid, from_time, to_time, format='pdf'):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'dashboardUid': dashboard_uid,
        'from': from_time,
        'to': to_time,
        'format': format
    }

    response = requests.post(f'{api_url}/api/report', headers=headers, json=payload)

    if response.status_code == 200:
        report_url = response.json()['url']
        print(f'Report URL: {report_url}')
    else:
        print(f'Error generating the report. Status code: {response.status_code}, Error message: {response.text}')

if __name__ == '__main__':
    api_url = 'http://your_grafana_instance_url'
    api_key = 'your_grafana_api_key'
    dashboard_uid = 'your_dashboard_uid'
    from_time = '2023-08-01T00:00:00Z'
    to_time = '2023-08-02T00:00:00Z'
    format = 'pdf'

    generate_grafana_report(api_url, api_key, dashboard_uid, from_time, to_time, format)
    