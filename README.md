ErrGrafanaAlert
===============

This repository contains a plugin for [ErrBot](http://errbot.io), which accepts [Grafana](https://grafana.com/) alerts via Grafanas webhook alerting.

**Please be aware, that is project is currently developed and is not fully functional yet!**

Setup
-----

To install ErrGrafanaAlert to your ErrBot, you first need to install it with the integrated repository management for ErrBot and then configure it, to activate it.

```
!repos install FreakyBytes/err-grafana-alert
!plugin config GrafanaAlert {'TOKEN_LENGTH': 48}
```

Usage
-----

Once installed and configured, you may use any of the commands below.

### `!grafana list`
Lists all configured grafana instances

### `!grafana add $name --url $url --room $room --show-images true`
Adds an Grafana instance with `$name`

TODO
