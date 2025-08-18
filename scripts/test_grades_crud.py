import requests
import time
import sys

BASE = "http://127.0.0.1:5000/api/admin/grades"

def log(msg):
    print(msg, flush=True)


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    session = requests.Session()

    # 1) List grades
    log("1) GET /grades")
    r = session.get(BASE, timeout=10)
    log(f"  Status: {r.status_code}")
    assert_true(r.ok, "GET /grades failed")
    before_list = r.json() if r.content else []
    log(f"  Count before: {len(before_list)}")

    # 2) Create grade
    unique = int(time.time())
    payload = {
        "grade_name": f"Test Grade {unique}",
        "description": "Created by automated CRUD test",
        "is_active": True,
    }
    log("2) POST /grades")
    r = session.post(BASE, json=payload, timeout=10)
    log(f"  Status: {r.status_code} Body: {r.text}")
    assert_true(r.ok, "POST /grades failed")
    data = r.json()
    assert_true(data.get("success") is True and data.get("grade_id") is not None, "POST did not return success/grade_id")
    grade_id = data["grade_id"]

    # 3) Verify in list
    log("3) GET /grades (verify created)")
    r = session.get(BASE, timeout=10)
    assert_true(r.ok, "GET /grades after create failed")
    grades = r.json() or []
    created = next((g for g in grades if g.get("grade_id") == grade_id), None)
    assert_true(created is not None, "Created grade not found in list")

    # 4) Update grade
    update_payload = {
        "grade_name": f"Updated Grade {unique}",
        "description": "Updated by automated CRUD test",
        "is_active": False,
    }
    log(f"4) PUT /grades/{grade_id}")
    r = session.put(f"{BASE}/{grade_id}", json=update_payload, timeout=10)
    log(f"  Status: {r.status_code} Body: {r.text}")
    assert_true(r.ok, "PUT /grades/{id} failed")
    upd = r.json()
    assert_true(upd.get("success") is True, "Update did not return success")

    # 5) Verify update
    log("5) GET /grades (verify updated)")
    r = session.get(BASE, timeout=10)
    assert_true(r.ok, "GET /grades after update failed")
    grades = r.json() or []
    updated = next((g for g in grades if g.get("grade_id") == grade_id), None)
    assert_true(updated is not None, "Updated grade not found in list")
    assert_true(updated.get("grade_name") == update_payload["grade_name"], "grade_name not updated")
    assert_true(updated.get("description") == update_payload["description"], "description not updated")
    # MySQL connector may return 0/1 for booleans; accept both forms
    is_active_val = updated.get("is_active")
    assert_true(is_active_val in (False, 0), f"is_active not updated, got {is_active_val}")

    # 6) Delete
    log(f"6) DELETE /grades/{grade_id}")
    r = session.delete(f"{BASE}/{grade_id}", timeout=10)
    log(f"  Status: {r.status_code} Body: {r.text}")
    assert_true(r.ok, "DELETE /grades/{id} failed")
    dele = r.json()
    assert_true(dele.get("success") is True, "Delete did not return success")

    # 7) Verify deletion
    log("7) GET /grades (verify deleted)")
    r = session.get(BASE, timeout=10)
    assert_true(r.ok, "GET /grades after delete failed")
    grades = r.json() or []
    removed = next((g for g in grades if g.get("grade_id") == grade_id), None)
    assert_true(removed is None, "Deleted grade still present in list")

    log("\nAll Grades CRUD tests passed ✔")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"\nTest failed: {e}")
        sys.exit(1)
