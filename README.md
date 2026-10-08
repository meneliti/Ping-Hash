# 🛰️ Ping-Hash

**Distributed uptime prober with git-backed audit logs.**

Ping-Hash adalah alat monitoring ringan yang kami pakai secara internal untuk memantau status server-server milik perusahaan — apakah sedang **UP** atau **DOWN** — dengan menyimpan hasil tiap probe sebagai log ter-hash di repository ini. Setiap entri adalah *fingerprint* SHA-256 dari waktu probe, sehingga riwayat uptime sulit dipalsukan dan mudah diaudit.

## Kenapa Ping-Hash?

Solusi monitoring komersial (Datadog, Pingdom, UptimeRobot) mahal dan butuh dashboard tambahan. Kami butuh sesuatu yang:

- 💸 **Gratis** — hanya butuh VM kecil + repo git
- 📝 **Audit-friendly** — setiap probe tercatat permanen dengan hash kriptografis
- 🔍 **Transparan** — siapa pun di tim bisa melihat riwayat uptime langsung dari repo
- 🪶 **Tanpa dependensi** — Python stdlib murni, tanpa pip install apapun

## Cara Kerja

```
┌─────────────┐     probe      ┌──────────────┐
│  Server     │ ◄───────────── │  Ping-Hash   │
│  (target)   │ ─────────────► │  Daemon (VM) │
└─────────────┘     reply      └──────┬───────┘
                                      │ SHA-256(timestamp)
                                      ▼
                              ┌──────────────┐
                              │ logs/*.log   │
                              │ commit+push  │
                              └──────────────┘
```

1. Daemon menjalankan probe pada **interval acak 1–8 menit** (bukan cron tetap, supaya tidak mudah ditebak polanya).
2. Timestamp probe di-**hash SHA-256** sebagai fingerprint unik.
3. Hasil (status UP/WARN, RTT, emoji indikator) ditulis ke `logs/YYYY-MM-DD.log`.
4. Commit di-push ke `main` — setiap commit adalah satu periode monitoring.

## Format Log

Setiap baris di `logs/` punya struktur:

```
2026-10-08T04:16:25Z | 37a2e7a36a7a | 🟢 probe | status=up | rtt=142ms
│                    │             │         │           │
│                    │             │         │           └─ round-trip time
│                    │             │         └─ status probe (up / warn)
│                    │             └─ label probe acak
│                    └─ 12 digit pertama hash SHA-256
│
└─ timestamp UTC (ISO 8601)
```

**Indikator status:**

| Emoji | Arti |
|-------|------|
| 🟢 ✅ 🟩 🟦 🔵 ⚡ 🛰️ 📶 🌐 🧭 | UP — server responsif |
| 🟡 ⚠️ 🟠 📡 | WARN — RTT tinggi (>800ms), perlu diperiksa |

> Gunakan hash di kolom kedua untuk memverifikasi keaslian entri:
> `echo -n "2026-10-08T04:16:25Z" | sha256sum` → harus cocok dengan hash yang tercatat.

## Menjalankan Sendiri

```bash
# 1. Clone repo
git clone git@github.com:meneliti/Ping-Hash.git
cd Ping-Hash

# 2. Jalankan probe sekali (untuk test)
python3 ping_hash.py

# 3. Jalankan sebagai daemon (loop terus dengan delay acak)
bash daemon.sh
```

**Konfigurasi** — edit bagian atas `ping_hash.py`:

| Variabel | Default | Keterangan |
|----------|---------|------------|
| `REPO_DIR` | `~/ping-hash/repo` | lokasi repo git |
| `LOG_DIR` | `~/ping-hash/repo/logs` | folder output log |
| interval | 60–480 detik | delay acak antar-probe |

## Struktur Repo

```
Ping-Hash/
├── README.md          ← dokumen ini
├── ping_hash.py       ← probe engine (Python stdlib)
├── daemon.sh          ← loop daemon interval-acak
├── .gitignore
└── logs/              ← hasil probe harian (auto-generated)
    └── 2026-10-08.log
```

## Roadmap

- [ ] Notifikasi Telegram/Slack saat status DOWN berturut-turut
- [ ] Grafik uptime HTML otomatis dari log
- [ ] Multi-target: probe beberapa server sekaligus
- [ ] Retensi log 90 hari dengan auto-prune

## Lisensi

Internal tool — penggunaan terbatas untuk infrastruktur perusahaan.

---
*Maintained by Infrastructure Team · Last updated: 2026-10-08*
