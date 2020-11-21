# https-certificate-expiry-checker

This is a Python script for checking the expiry dates of website TLS/SSL certificates, used for creating secure HTTPS connections.

To use the script simply run it from the command line, along with a list of the domain names you wish to check. For example:

    > python check-certificates.py codebox.net www.codebox.net api.codebox.net oldtime.radio c0debox.net
    
    Checking 5 endpoints...
    codebox.net     OK    expires in 48 days
    www.codebox.net OK    expires in 48 days
    api.codebox.net OK    expires in 48 days
    oldtime.radio   WARN  expires in 6 days 21 hours 13 minutes
    c0debox.net     ERROR [Errno 8] nodename nor servname provided, or not known
 
The script will list the status of each domain's certificate, displaying '`OK`' if the certificate was retrieved and is not expiring soon, '`WARN`' if the certificate's expiry date is getting close, or '`ERROR`' if the certificate has already expired, or if there is some other problem such as the host could not be found, or no certificate could be retrieved.

By default '`WARN`' will be displayed if there are less than 7 days until a certificate expires, but this interval can be changed by altering the value of the [WARN_IF_DAYS_LESS_THAN](https://github.com/codebox/https-certificate-expiry-checker/blob/main/check-certificates.py#L13) variable.
 
If any of the domains are using a non-standard port for HTTPS then this should be specified using the usual notation of `host:port`, for example:

    > python check-certificates.py test.codebox.net:8443

The script returns an exit code indicating whether the checks passed or not, making it easier to take appropriate action in a shell script (for example, send a email if the checks fail):

| Condition | Exit Code |
|-----------|-----------|
| Everything is fine, none of the certificates are expiring soon | 0 |
| At least one certificate is expiring soon | 1 |
| At least one certificate has expired, is invalid, or could not be retrieved | 2 |
| Both of the previous conditions occurred | 3 |
| No domain list was provided when running the script | 9 |
 
Certificate checks are performed in parallel, making the process of checking multiple domains much quicker. The number of concurrent checks that will be performed is determined by the value of the [WORKER_THREAD_COUNT](https://github.com/codebox/https-certificate-expiry-checker/blob/main/check-certificates.py#L11) variable.
  