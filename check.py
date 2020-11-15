import sys
import multiprocessing
import ssl
import socket
import datetime
import concurrent.futures


DEFAULT_HTTPS_PORT = 443
WORKER_THREAD_COUNT = multiprocessing.cpu_count()
SOCKET_CONNECTION_TIMEOUT_SECONDS = 10

def make_host_port_pair(endpoint):
    host, _, specified_port = endpoint.partition(':')
    port = int(specified_port or DEFAULT_HTTPS_PORT)

    return host, port

def pluralise(singular, count):
    return '{} {}{}'.format(count, singular, '' if count == 1 else 's')

def get_certificate_expiry_date_time(context, host, port):
    with socket.create_connection((host, port), SOCKET_CONNECTION_TIMEOUT_SECONDS) as tcp_socket:
        with context.wrap_socket(tcp_socket, server_hostname=host) as ssl_socket:
            # certificate_info is a dict with lots of information about the certificate
            certificate_info = ssl_socket.getpeercert()
            exp_date_text = certificate_info['notAfter']
            # date format is like 'Sep  9 12:00:00 2016 GMT'
            return datetime.datetime.strptime(exp_date_text, r'%b %d %H:%M:%S %Y %Z')


def format_time_remaining(expiry_time):
    time_remaining = expiry_time - datetime.datetime.utcnow()
    day_count = time_remaining.days

    if day_count >= 7:
        return pluralise('day', day_count)

    else:
        seconds_per_minute = 60
        seconds_per_hour = seconds_per_minute * 60
        seconds_unaccounted_for = time_remaining.seconds

        hours = int(seconds_unaccounted_for / seconds_per_hour)
        seconds_unaccounted_for -= hours * seconds_per_hour

        minutes = int(seconds_unaccounted_for / seconds_per_minute)

        return '{} {} {}'.format(
            pluralise('day', day_count),
            pluralise('hour', hours),
            pluralise('min', minutes)
        )

def check_certificates(endpoints):
    context = ssl.create_default_context()
    host_port_pairs = [make_host_port_pair(endpoint) for endpoint in endpoints]

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKER_THREAD_COUNT) as executor:
        futures = {
            executor.submit(get_certificate_expiry_date_time, context, host, port): (host, port)
            for host, port in host_port_pairs
        }

        endpoint_count = len(endpoints)
        print('Checking {}...'.format(pluralise('endpoint', endpoint_count)))
        for future in concurrent.futures.as_completed(futures):
            host, port = futures[future]
            try:
                expiry_time = future.result()
            except Exception as ex:
                print('{}:{} ERROR: {}'.format(host, port, ex))
            else:
                time_remaining = format_time_remaining(expiry_time)
                print('{}:{} expires in {}'.format(host, port, time_remaining))


if __name__ == '__main__':
    endpoints = sys.argv[1:]

    if len(endpoints):
        check_certificates(endpoints)
    else:
        print('Usage: {} <list of endpoints>'.format(sys.argv[0]))


