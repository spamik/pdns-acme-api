# PowerDNS API proxy for ACME requests


Simple REST API written in Python which acts like a proxy for PowerDNS WEB API.

Why? There are several ways for obtaining SSL certificate from Let's Encrypt or other providers. The most common is authorization via HTTP published file (challenge from ACME server is published on HTTP server on same hostname). But there are some cases where this can't be used, e.g:
- you can't have opened TCP port 80. For example you have several virtual machines behind one public IP and this port is already used. Or you just don't want to install any HTTP server.
- you want receive SSL certificate for internal hostname which it's not accessible from the internet (or even the DNS records for these hostnames can be only on internal nameserver). And you want use LE or similar because it's still much easier solution than running own CA.

In these cases there is an option: DNS authorization. Challenge from ACME server is published in public DNS as TXT record. If you look for example on acme.sh client, it has several plugins for auto deployments these challenges to DNS for several DNS providers. But when you are running your own nameservers... you can use PowerDNS! PowerDNS has builtin REST API, acme.sh client has plugin for it, everything is running fine...

... until you start thinking about security. Authorization to PowerDNS WEB API is done via token, which is set in pdns.conf file. This token is then transmitted in requests via X-API-Key HTTP header. Only one token. So all clients requiring SSL certificates shares this one token. And even worse: via this API you can do everything on this DNS server. You can change, delete or add any record. And compromising one host then compromise all DNS zones on this server. Even when you are using it only for non-public DNS zone via NS delegation, it's still problem when attacker can get valid certificate for any host in internal zone after compromising one host.

So why this proxy? It implements the minimum features from PowerDNS WEB API to be compatible with ACME clients (like acme.sh pdns plugin). But it has own database with access tokens. Means that each one host has unique token and no one of them knows the actual PowerDNS token (even PowerDNS WEB API must be visible to this proxy but not the hosts). Moreover for each host/token you have to specify domain names for which the host can ask for certificates. Thanks for this list requests are filtered to these names (so it's not possible to dump whole DNS zone) and change requests which contains unauthorized names are denied.

## Prerequisites

Working and running PowerDNS server. With enabled WEB API. Namely pay attention to these options in pdns.conf:
- webserver=yes (to enable API)
- webserver-allow-from= address from this cames reqeusts from this API must be included here
- webserver-port - port on which is API running, need later
- api-key - token for requests. Needs to be long, random, secure

## Configuration and running
Dockerfile is included in this repo, so easiest way to run this API is using docker. Copy docker-compose.yml.example file and adjust it to your needs. Configuration is done via few environment variables:
- PDNS_ADDRESS - URL to PowerDNS WEB API including HTTP port. For example, if pDNS server is running on host my-ns.com on port 8081, it would be http://my-ns.com:8081
- PDNS_TOKEN - api key variable from pdns.com
- ADMIN_TOKEN - token/key for managing requests to this API. This token you need for managing hosts and theirs DNS records. Also use some random, long, secure string
- DATABASE_URL - SQLAlchemy URL for database connection. This is optional, default value stores data in SQLite database in named volume created in docker-compose file. But you can adjust it if you need. With some modification (probably installation python database drivers) you can save data in SQL database. Database is needed for storing host tokens and domains.

Now just build image and run it:

```
docker compose build
docker compose up
```

## Working with API

You have to use few internal API endpoints for managing API. Mainly creating (or changing/deleting) hosts with their tokens and their mapped DNS records. In all requests must be set X-API-Key header with value configured in ADMIN_TOKEN environment variable.

You can visit /docs URL to see all endpoints in swagger UI. You can also submit requests from there. For quick summary there are these endpoints:

- GET /acme-api/hosts - returns all configured hosts with theirs DNS records
- GET /acme-api/hosts/{host_id}/ - return details about host with ID host_id
- DELETE /acme-api/hosts/{host_id}/ - delete host (including his DNS records) with this ID
- PUT /acme-api/hosts/{host_id}/ - change host token (API key)
- POST /acme-api/hosts/{host_id}/domain_maps/ - add new allowed DNS record for this host
- DELETE /acme-api/domain-maps/{domain_map_id}/ - delete this binded DNS record

Note that host access token serves also as a host identification. For this reason, token must be unique. This shouldn't be limitation as these should really be long, random strings and also this API will be probably maintained by one or few administrators.