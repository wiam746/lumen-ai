from conftest import db_query, make_user, post
from lumen import audit
from lumen.db import connect
from lumen.retention import purge_expired


def test_audit_chain_is_intact_then_detects_tampering(app):
    c = make_user(app, "alice")
    post(c, "/ask", {"prompt": "what is gdpr"})
    conn = connect(app.config["DATABASE_PATH"])
    ok, checked, broken = audit.verify(conn)
    assert ok and checked >= 3 and broken is None
    conn.execute("UPDATE audit_events SET action='NOTHING_TO_SEE' WHERE id=2")
    conn.commit()
    ok, _, broken = audit.verify(conn)
    assert not ok and broken == 2
    conn.close()


def test_audit_has_no_message_content_or_usernames(app):
    c = make_user(app, "visible-name")
    post(c, "/ask", {"prompt": "unique-marker-phrase about gdpr"})
    dump = " ".join(" ".join(map(str, r)) for r in db_query(app, "SELECT * FROM audit_events"))
    assert "unique-marker-phrase" not in dump and "visible-name" not in dump


def test_audit_ip_is_truncated(app):
    make_user(app, "alice")
    ips = {r[0] for r in db_query(app, "SELECT ip_masked FROM audit_events")}
    assert ips and all(ip.endswith("/24") or ip == "-" for ip in ips)


def test_retention_purge_deletes_only_expired_data(app):
    c = make_user(app, "alice")
    post(c, "/ask", {"prompt": "what is gdpr"})
    conn = connect(app.config["DATABASE_PATH"])
    conn.execute("INSERT INTO requests (user_id, prompt_enc, response_enc, provider, model, created_at) "
                 "VALUES (1, 'x', 'y', 'offline', 'm', datetime('now', '-200 days'))")
    conn.execute("INSERT INTO audit_events (created_at, actor, action, prev_hash, hash) "
                 "VALUES (datetime('now','-400 days'), 'system', 'OLD', 'p', 'h')")
    conn.commit()
    with app.app_context():
        from flask import g
        counts = purge_expired(conn)
    assert counts["requests"] == 1 and counts["audit_events"] == 1
    assert conn.execute("SELECT COUNT(*) FROM requests").fetchone()[0] == 1
    conn.close()


def test_encryption_key_rotation(app):
    from cryptography.fernet import Fernet
    from lumen import crypto
    with app.app_context():
        token = crypto.encrypt("secret text")
        new_key = Fernet.generate_key().decode()
        app.config["DATA_ENCRYPTION_KEY"] = new_key + "," + app.config["DATA_ENCRYPTION_KEY"]
        crypto.init_app(app)
        assert crypto.decrypt(token) == "secret text"
        assert crypto.decrypt(crypto.encrypt("new")) == "new"
