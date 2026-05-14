# Expose OSCAR WSL MariaDB to Another Machine

This guide explains how to expose an OSCAR EMR MariaDB server running inside WSL on a Windows machine so `oscaremr-mcp` can connect from another trusted device on the same LAN.

Use this only on a trusted private network. Do not expose MariaDB directly to the public internet.

## What This Does

WSL normally has its own internal IP address. Other devices on your LAN usually cannot connect to that WSL IP directly. The Windows host must forward a LAN-facing port to the MariaDB port inside WSL.

The setup has three parts:

- Make MariaDB listen on WSL interfaces.
- Forward Windows `0.0.0.0:3306` to WSL `<wsl-ip>:3306`.
- Allow inbound TCP `3306` through Windows Firewall.

## 1. Open PowerShell as Administrator

On the Windows machine where OSCAR EMR is running in WSL, open PowerShell as Administrator.

List WSL distros:

```powershell
wsl -l -v
```

If your OSCAR distro is not `Ubuntu-22.04`, replace `Ubuntu-22.04` in the commands below with the exact distro name.

## 2. Start MariaDB and Allow External Binding

Run:

```powershell
wsl -d Ubuntu-22.04 -u root -- bash -lc "sed -i 's/^\s*bind-address\s*=.*/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf && (systemctl restart mariadb || service mariadb restart)"
```

Verify MariaDB is listening inside WSL:

```powershell
wsl -d Ubuntu-22.04 -u root -- bash -lc "ss -ltnp | grep ':3306' || netstat -ltnp | grep ':3306'"
```

Expected result includes `0.0.0.0:3306` or another listener on port `3306`.

## 3. Get the Current WSL IP

Run:

```powershell
$wslIp = (wsl -d Ubuntu-22.04 hostname -I).Trim().Split(" ")[0]
Write-Host "WSL IP: $wslIp"
```

WSL IP addresses can change after reboot, shutdown, VPN changes, or network changes. If the connection later stops working, rerun this section and refresh the portproxy rule.

## 4. Add Windows Port Forwarding

Delete any stale rule first. It is okay if this command says the rule does not exist:

```powershell
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=3306
```

Add a new rule to forward Windows port `3306` to WSL MariaDB:

```powershell
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=3306 connectaddress=$wslIp connectport=3306
```

Show the active rule:

```powershell
netsh interface portproxy show v4tov4
```

Expected output should include:

```text
0.0.0.0  3306  <wsl-ip>  3306
```

## 5. Allow Windows Firewall Inbound Access

Create the firewall rule:

```powershell
New-NetFirewallRule -DisplayName "Allow OSCAR MariaDB 3306" -Direction Inbound -Protocol TCP -LocalPort 3306 -Action Allow
```

If the rule already exists, PowerShell may create a duplicate. To inspect existing rules:

```powershell
Get-NetFirewallRule -DisplayName "Allow OSCAR MariaDB 3306" | Select-Object DisplayName,Enabled,Direction,Action
```

## 6. Verify From the OSCAR Windows Host

Get the Windows host LAN IP:

```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.254*' -and $_.IPAddress -ne '127.0.0.1' } | Select-Object InterfaceAlias,IPAddress,PrefixLength
```

Then test locally:

```powershell
Test-NetConnection 127.0.0.1 -Port 3306
Test-NetConnection <windows-lan-ip> -Port 3306
```

Expected:

```text
TcpTestSucceeded : True
```

## 7. Verify From the MCP Client Machine

On the machine where `oscaremr-mcp` will run:

```powershell
Test-NetConnection <oscar-windows-lan-ip> -Port 3306
```

Expected:

```text
TcpTestSucceeded : True
```

If this succeeds, configure `.env` in `oscaremr-mcp`:

```dotenv
OSCAR_MCP_MYSQL_HOST=<oscar-windows-lan-ip>
OSCAR_MCP_MYSQL_PORT=3306
OSCAR_MCP_MYSQL_DATABASE=oscar_15
OSCAR_MCP_MYSQL_USER=<readonly-user>
OSCAR_MCP_MYSQL_PASSWORD=<password>
```

Then test the MCP database client:

```powershell
@'
from oscar_db_mcp.db import OscarDbClient

client = OscarDbClient()
print(client.health_check())
print(client.list_tables()[:20])
'@ | python -
```

## Refresh After WSL IP Changes

If WSL gets a new IP, run this again on the OSCAR Windows host:

```powershell
$wslIp = (wsl -d Ubuntu-22.04 hostname -I).Trim().Split(" ")[0]
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=3306
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=3306 connectaddress=$wslIp connectport=3306
netsh interface portproxy show v4tov4
```

## Remove Access

To remove the port forwarding rule:

```powershell
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=3306
```

To remove the firewall rule:

```powershell
Remove-NetFirewallRule -DisplayName "Allow OSCAR MariaDB 3306"
```

## Troubleshooting

`TcpTestSucceeded` is `False` from the MCP machine:

- Confirm the OSCAR Windows host is reachable with `Test-Connection <oscar-windows-lan-ip>`.
- Confirm the Windows LAN IP is correct.
- Confirm the portproxy rule points to the current WSL IP.
- Confirm Windows Firewall allows inbound TCP `3306`.
- Confirm MariaDB is listening inside WSL on port `3306`.
- Check VPN, subnet isolation, or router firewall rules.

`Access denied for user`:

- The network path is working, but MariaDB rejected the credentials.
- Confirm the user exists for remote hosts, such as `'user'@'%'`, or use an account configured for the connecting host.
- Prefer a read-only database user for MCP inspection workflows.

`Lost connection during query`:

- Confirm the account can connect from the MCP client machine.
- Confirm MariaDB is not bound only to `127.0.0.1`.
- Confirm portproxy points to the current WSL IP.

## Security Notes

- Keep this on a trusted private network.
- Do not expose `3306` to the public internet.
- Prefer a read-only MariaDB user for MCP access.
- Use admin/root credentials only for intentional local maintenance.
- Follow your clinic or organization privacy rules before querying health data.
