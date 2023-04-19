# 1.0.17

* [*] Added ability to list site event notifications (alerts) for a specified website.

# 1.0.16

* [*] Added ability to calculate and print the uptime for a specified site for a custom time period or the last 24 hours, 1 week, 30 days, a quarter or a year.
* [*] Added ability to print the daily or monthly average uptime in a table for the specified time period or the total time span available (for each month since start).
* [*] Added ability to list server event notifications (alerts) for a specified server.

# 1.0.14

* [*] Added ability to add incidents and list them for a given status page.
* [*] Added ability to create magic links for specific readonly server dashboards.
* [*] Added check for latest version to recommend using the latest version if the local one is outdated.
* [*] Improved server query speed for filtered servers by tags by specifying the tags as query parameter.

# 1.0.13

* [*] Added columns "Name" and "Tags" for user tokens.
* [*] Added "recommendations" command to display upgrade recommendations for servers that have exceeded their limits for the current workload.
* [*] Added "wptoolkit" command to list statistics about WordPress sites and issues with those from servers that run WP Toolkit.

# 1.0.11

* [*] Added option to limit the number of printed items with --limit n.
* [*] Added option to sort items in a table according to the specified criteria with --sort COLUMN --reverse.

# 1.0.10

* [*] Added "signup" command to get your 360 Monitoring account if you don't have one yet.
* [*] Added "dashboard" command to open 360 Monitoring in your Web Browser.

# 1.0.9

* [*] Now you can show only sites or servers that have issues with "list --issues".
* [-] Fixed Bug: exception thrown if "ip_whois" contains no information.
# 1.0.7

* [*] Print more data for servers. Added ability to set tags for specified servers. Added more statistics.
# 1.0.4

* [*] Added "statistics" command.

# 1.0.1

* [*] Added support for PyPy to simplify installing 360 Monitoring CLI via pip.
* [*] Added thresholds for uptime and ttfb to print values not matching the expected threshold in red.
