# Pre-built Wheels

In case uv refuses to resolve certain wheels, download and place them in this directory.
In my case, this applied to `pillow`, `spidev`, and `rpi-gpio`.

```toml
[tool.uv]
index-url = "https://piwheels.org/simple"
```