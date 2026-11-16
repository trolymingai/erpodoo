#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ming Coffee - Odoo ERP Operations CLI Tool
High-speed internal CLI for Ming AI to manage tasks, checklists, and employee onboarding.
Fully synchronizes staff checklists and operational tasks to Odoo ERP 19.
"""

import sys
import os
import json
import datetime
import xmlrpc.client

ODOO_URL = "http://172.18.0.1:18070"
ODOO_DB = "odoo_minghouse"
ODOO_UID = 2
ODOO_API_KEY = "1362a613017363da65d6cbb7b3c831fa68a7a71e"

def get_models():
    return xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

def get_vn_time():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_vn = now_utc + datetime.timedelta(hours=7)
    return now_vn.strftime("%Y-%m-%d %H:%M:%S")

def list_branches():
    models = get_models()
    branches = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "ming.branch", "search_read", [[]],
        {"fields": ["id", "name", "code", "brand"]}
    )
    print(json.dumps({"status": "success", "data": branches}, ensure_ascii=False, indent=2))

def list_projects():
    models = get_models()
    projects = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "project.project", "search_read", [[]],
        {"fields": ["id", "name"]}
    )
    print(json.dumps({"status": "success", "data": projects}, ensure_ascii=False, indent=2))

def find_project_id(identifier):
    models = get_models()
    try:
        pid = int(identifier)
        return pid
    except ValueError:
        pass
    
    clean_id = identifier.upper().strip()
    proj_map = {
        "A3": "Vận Hành - Ming A3 (Liên Hương)",
        "MING-A3": "Vận Hành - Ming A3 (Liên Hương)",
        "MING A3": "Vận Hành - Ming A3 (Liên Hương)",
        "LH": "Vận Hành - Ming Liên Hương",
        "MING-LH": "Vận Hành - Ming Liên Hương",
        "MING LIÊN HƯƠNG": "Vận Hành - Ming Liên Hương",
        "PR": "Vận Hành - Ming Phan Rí",
        "MING-PR": "Vận Hành - Ming Phan Rí",
        "MING PHAN RÍ": "Vận Hành - Ming Phan Rí",
        "LD": "Vận Hành - GOO-LD",
        "GOO-LD": "Vận Hành - GOO-LD",
        "A2": "Vận Hành - GOO-A2",
        "GOO-A2": "Vận Hành - GOO-A2"
    }
    target_name = proj_map.get(clean_id, identifier)
    projects = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "project.project", "search_read",
        [[["name", "ilike", target_name]]],
        {"fields": ["id", "name"]}
    )
    if projects:
        return projects[0]["id"]
    return 1 # default to general

def find_employee(emp_identifier):
    if not emp_identifier:
        return None
    models = get_models()
    query = str(emp_identifier).strip()
    domain = [
        "|", "|", "|", "|",
        ["name", "ilike", query],
        ["work_phone", "ilike", query],
        ["mobile_phone", "ilike", query],
        ["work_email", "ilike", query],
        ["additional_note", "ilike", query]
    ]
    employees = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "hr.employee", "search_read",
        [domain],
        {"fields": ["id", "name", "work_phone", "mobile_phone", "work_email", "user_id", "department_id"]}
    )
    if employees:
        emp = employees[0]
        user_id = emp["user_id"][0] if emp.get("user_id") else None
        phone = emp["work_phone"] or emp["mobile_phone"] or ""
        dept = emp["department_id"][1] if emp.get("department_id") else ""
        return {
            "id": emp["id"],
            "user_id": user_id,
            "name": emp["name"],
            "phone": phone,
            "email": emp["work_email"] or "",
            "department": dept
        }
    return None

def get_tasks(project_id_or_name=None):
    models = get_models()
    domain = []
    if project_id_or_name:
        pid = find_project_id(project_id_or_name)
        domain.append(["project_id", "=", pid])
    
    tasks = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "project.task", "search_read",
        [domain],
        {"fields": ["id", "name", "project_id", "stage_id", "state", "user_ids", "create_date", "write_date", "description"], "limit": 20, "order": "id desc"}
    )
    print(json.dumps({"status": "success", "count": len(tasks), "data": tasks}, ensure_ascii=False, indent=2))

def create_task(project_id_or_name, title, description="", emp_identifier=None):
    models = get_models()
    pid = find_project_id(project_id_or_name)
    now_vn = get_vn_time()
    
    vals = {
        "name": title,
        "project_id": pid,
        "stage_id": 1, # Hộp thư đến
        "state": "01_in_progress"
    }
    
    emp_info = find_employee(emp_identifier) if emp_identifier else None
    if emp_info:
        if emp_info.get("user_id"):
            vals["user_ids"] = [(4, emp_info["user_id"])]
        desc_extra = f"<p><strong>Nhân sự phụ trách:</strong> {emp_info['name']} ({emp_info['phone']}) - {emp_info['department']}<br/><strong>Thời gian giao:</strong> {now_vn}</p>"
        vals["description"] = f"<p>{description}</p>{desc_extra}" if description else desc_extra
    else:
        if description:
            vals["description"] = f"<p>{description}</p>"

    task_id = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "project.task", "create",
        [vals]
    )
    
    # Post chatter
    chatter_msg = f"📋 <b>Giao việc / Checklist ca mới</b><br/>- Tiêu đề: {title}<br/>- Thời gian: {now_vn}"
    if emp_info:
        chatter_msg += f"<br/>- Người thực hiện: <b>{emp_info['name']}</b> ({emp_info['phone']})"
    try:
        models.execute_kw(
            ODOO_DB, ODOO_UID, ODOO_API_KEY,
            "project.task", "message_post",
            [[task_id]],
            {"body": chatter_msg, "message_type": "comment"}
        )
    except Exception:
        pass

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "title": title,
        "project_id": pid,
        "assigned_to": emp_info["name"] if emp_info else None,
        "message": f"Tạo task #{task_id} thành công trên Odoo ERP."
    }, ensure_ascii=False, indent=2))

def complete_task(task_id, emp_identifier=None, note=""):
    models = get_models()
    task_id = int(task_id)
    now_vn = get_vn_time()
    emp_info = find_employee(emp_identifier) if emp_identifier else None
    
    vals = {
        "stage_id": 6, # Hoàn tất
        "state": "1_done"
    }
    
    if emp_info and emp_info.get("user_id"):
        vals["user_ids"] = [(4, emp_info["user_id"])]
        
    models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "project.task", "write",
        [[task_id], vals]
    )
    
    # Post chatter
    chatter_msg = f"✅ <b>Hoàn tất checklist qua Zalo</b><br/>- Thời gian hoàn tất: {now_vn}"
    if emp_info:
        chatter_msg += f"<br/>- Nhân sự hoàn tất: <b>{emp_info['name']}</b> ({emp_info['phone']})"
    if note:
        chatter_msg += f"<br/>- Ghi chú / Báo cáo: {note}"
        
    try:
        models.execute_kw(
            ODOO_DB, ODOO_UID, ODOO_API_KEY,
            "project.task", "message_post",
            [[task_id]],
            {"body": chatter_msg, "message_type": "comment"}
        )
    except Exception:
        pass

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "completed_by": emp_info["name"] if emp_info else "Nhân viên",
        "message": f"Task #{task_id} đã cập nhật sang trạng thái Hoàn tất trên Odoo ERP."
    }, ensure_ascii=False, indent=2))

def sync_checklist(branch, title, emp_identifier, status="done", note=""):
    """
    High-level smart sync for staff checklist:
    Searches existing task by title in branch project.
    If found -> updates stage and logs completion.
    If not found -> creates new task and marks done with employee attribution.
    """
    models = get_models()
    pid = find_project_id(branch)
    emp_info = find_employee(emp_identifier) if emp_identifier else None
    now_vn = get_vn_time()
    
    # Search today's task matching title
    existing = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "project.task", "search_read",
        [[["project_id", "=", pid], ["name", "ilike", title.strip()]]],
        {"fields": ["id", "name", "stage_id", "state"], "limit": 1, "order": "id desc"}
    )
    
    if existing:
        task_id = existing[0]["id"]
        vals = {}
        if status.lower() in ["done", "hoantat", "hoàn tất", "ok"]:
            vals["stage_id"] = 6 # Hoàn tất
            vals["state"] = "1_done"
        if emp_info and emp_info.get("user_id"):
            vals["user_ids"] = [(4, emp_info["user_id"])]
            
        if vals:
            models.execute_kw(
                ODOO_DB, ODOO_UID, ODOO_API_KEY,
                "project.task", "write",
                [[task_id], vals]
            )
            
        chatter = f"✅ <b>Checklist ca được đồng bộ từ Zalo</b><br/>- Nhân viên: <b>{emp_info['name'] if emp_info else emp_identifier}</b><br/>- Trạng thái: Hoàn tất<br/>- Thời gian: {now_vn}"
        if note:
            chatter += f"<br/>- Ghi chú: {note}"
        try:
            models.execute_kw(ODOO_DB, ODOO_UID, ODOO_API_KEY, "project.task", "message_post", [[task_id]], {"body": chatter, "message_type": "comment"})
        except Exception:
            pass
            
        print(json.dumps({
            "status": "success",
            "action": "updated",
            "task_id": task_id,
            "title": existing[0]["name"],
            "branch": branch,
            "employee": emp_info["name"] if emp_info else emp_identifier,
            "stage": "Hoàn tất",
            "message": f"Đã đồng bộ hoàn tất checklist #{task_id} lên Odoo ERP cho {emp_info['name'] if emp_info else emp_identifier}."
        }, ensure_ascii=False, indent=2))
        return
        
    # If not existing, create directly
    is_done = status.lower() in ["done", "hoantat", "hoàn tất", "ok"]
    new_vals = {
        "name": title.strip(),
        "project_id": pid,
        "stage_id": 6 if is_done else 1,
        "state": "1_done" if is_done else "01_in_progress",
        "description": f"<p>{note}</p><p><strong>Nhân sự:</strong> {emp_info['name'] if emp_info else emp_identifier}<br/><strong>Thời gian:</strong> {now_vn}</p>"
    }
    if emp_info and emp_info.get("user_id"):
        new_vals["user_ids"] = [(4, emp_info["user_id"])]
        
    task_id = models.execute_kw(ODOO_DB, ODOO_UID, ODOO_API_KEY, "project.task", "create", [new_vals])
    
    chatter = f"✅ <b>Checklist ca mới đồng bộ từ Zalo</b><br/>- Nhân viên: <b>{emp_info['name'] if emp_info else emp_identifier}</b><br/>- Trạng thái: {'Hoàn tất' if is_done else 'Đang xử lý'}<br/>- Thời gian: {now_vn}"
    if note:
        chatter += f"<br/>- Báo cáo: {note}"
    try:
        models.execute_kw(ODOO_DB, ODOO_UID, ODOO_API_KEY, "project.task", "message_post", [[task_id]], {"body": chatter, "message_type": "comment"})
    except Exception:
        pass
        
    print(json.dumps({
        "status": "success",
        "action": "created_and_synced",
        "task_id": task_id,
        "title": title,
        "branch": branch,
        "employee": emp_info["name"] if emp_info else emp_identifier,
        "stage": "Hoàn tất" if is_done else "Đang xử lý",
        "message": f"Đã tạo mới và đồng bộ thành công task #{task_id} lên Odoo ERP."
    }, ensure_ascii=False, indent=2))

def get_staff_tasks(emp_identifier):
    models = get_models()
    emp_info = find_employee(emp_identifier)
    if not emp_info or not emp_info.get("user_id"):
        print(json.dumps({
            "status": "error",
            "message": f"Không tìm thấy tài khoản nhân viên cho: {emp_identifier}"
        }, ensure_ascii=False, indent=2))
        return
        
    tasks = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "project.task", "search_read",
        [[["user_ids", "in", [emp_info["user_id"]]]]],
        {"fields": ["id", "name", "project_id", "stage_id", "state", "create_date", "write_date"], "limit": 20, "order": "id desc"}
    )
    print(json.dumps({
        "status": "success",
        "employee": emp_info["name"],
        "count": len(tasks),
        "data": tasks
    }, ensure_ascii=False, indent=2))

def find_department_by_branch(branch_str):
    models = get_models()
    branch_map = {
        "A3": "Chi nhánh Ming A3 (Liên Hương)",
        "MING-A3": "Chi nhánh Ming A3 (Liên Hương)",
        "LH": "Chi nhánh Ming Liên Hương",
        "MING-LH": "Chi nhánh Ming Liên Hương",
        "PR": "Chi nhánh Ming Phan Rí",
        "MING-PR": "Chi nhánh Ming Phan Rí",
        "LD": "Chi nhánh GOO-LD",
        "GOO-LD": "Chi nhánh GOO-LD",
        "A2": "Chi nhánh GOO-A2",
        "GOO-A2": "Chi nhánh GOO-A2"
    }
    target_name = branch_map.get(branch_str.upper().strip(), branch_str)
    depts = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "hr.department", "search_read",
        [[["name", "ilike", target_name]]],
        {"fields": ["id", "name"]}
    )
    if depts:
        return depts[0]["id"], depts[0]["name"]
    return 7, "Khối Vận Hành & Barista"

def onboard_employee(name, phone, email, branch_code, work_schedule=""):
    models = get_models()
    name = name.strip()
    phone = phone.strip()
    email = email.strip().lower()
    
    domain = []
    if phone and email:
        domain = ["|", ["work_phone", "=", phone], ["work_email", "=", email]]
    elif phone:
        domain = [["work_phone", "=", phone]]
    elif email:
        domain = [["work_email", "=", email]]
        
    existing = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "hr.employee", "search_read",
        [domain],
        {"fields": ["id", "name", "work_phone", "work_email", "department_id"]}
    ) if domain else []
    
    dept_id, dept_name = find_department_by_branch(branch_code)
    
    if existing:
        emp_id = existing[0]["id"]
        models.execute_kw(
            ODOO_DB, ODOO_UID, ODOO_API_KEY,
            "hr.employee", "write",
            [[emp_id], {
                "department_id": dept_id,
                "additional_note": f"Giờ làm việc: {work_schedule}" if work_schedule else ""
            }]
        )
        print(json.dumps({
            "status": "exists",
            "employee_id": emp_id,
            "name": existing[0]["name"],
            "department": dept_name,
            "message": f"Nhân viên đã tồn tại trên Odoo (ID: {emp_id}). Đã cập nhật chi nhánh/giờ làm."
        }, ensure_ascii=False, indent=2))
        return

    emp_vals = {
        "name": name,
        "work_phone": phone,
        "mobile_phone": phone,
        "work_email": email,
        "department_id": dept_id,
        "additional_note": f"Giờ làm việc: {work_schedule}" if work_schedule else ""
    }
    emp_id = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "hr.employee", "create",
        [emp_vals]
    )

    user_id = None
    if email:
        users = models.execute_kw(
            ODOO_DB, ODOO_UID, ODOO_API_KEY,
            "res.users", "search_read",
            [[["login", "=", email]]],
            {"fields": ["id"]}
        )
        if users:
            user_id = users[0]["id"]
        else:
            try:
                user_id = models.execute_kw(
                    ODOO_DB, ODOO_UID, ODOO_API_KEY,
                    "res.users", "create",
                    [{
                        "name": name,
                        "login": email,
                        "email": email,
                        "notification_type": "email"
                    }]
                )
            except Exception:
                pass

    if user_id:
        try:
            models.execute_kw(
                ODOO_DB, ODOO_UID, ODOO_API_KEY,
                "hr.employee", "write",
                [[emp_id], {"user_id": user_id}]
            )
        except Exception:
            pass

    print(json.dumps({
        "status": "success",
        "employee_id": emp_id,
        "user_id": user_id,
        "name": name,
        "phone": phone,
        "email": email,
        "department": dept_name,
        "work_schedule": work_schedule,
        "message": f"Tạo hồ sơ nhân viên thành công trên Odoo ERP (ID: {emp_id})."
    }, ensure_ascii=False, indent=2))

def search_employee(query):
    models = get_models()
    query = query.strip()
    domain = ["|", "|", "|", ["name", "ilike", query], ["work_phone", "ilike", query], ["mobile_phone", "ilike", query], ["work_email", "ilike", query]]
    employees = models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "hr.employee", "search_read",
        [domain],
        {"fields": ["id", "name", "work_phone", "mobile_phone", "work_email", "department_id", "job_title", "user_id"]}
    )
    print(json.dumps({"status": "success", "count": len(employees), "data": employees}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: odoo_cli <command> [args...]")
        print("Commands:")
        print("  list_branches")
        print("  list_projects")
        print("  get_tasks [project_id_or_branch]")
        print("  create_task <branch/project> <title> [desc] [employee]")
        print("  complete_task <task_id> [employee] [note]")
        print("  sync_checklist <branch> <title> <employee> [status] [note]")
        print("  get_staff_tasks <employee>")
        print("  onboard_employee <name> <phone> <email> <branch> [schedule]")
        print("  search_employee <query>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "list_branches":
        list_branches()
    elif cmd == "list_projects":
        list_projects()
    elif cmd == "get_tasks" or cmd in ["get_branch_status", "branch_status"]:
        pid = sys.argv[2] if len(sys.argv) > 2 else None
        get_tasks(pid)
    elif cmd == "create_task":
        if len(sys.argv) < 4:
            print("Error: create_task requires <project/branch> <title> [desc] [employee]")
            sys.exit(1)
        desc = sys.argv[4] if len(sys.argv) > 4 else ""
        emp = sys.argv[5] if len(sys.argv) > 5 else None
        create_task(sys.argv[2], sys.argv[3], desc, emp)
    elif cmd == "complete_task":
        if len(sys.argv) < 3:
            print("Error: complete_task requires <task_id> [employee] [note]")
            sys.exit(1)
        emp = sys.argv[3] if len(sys.argv) > 3 else None
        note = sys.argv[4] if len(sys.argv) > 4 else ""
        complete_task(sys.argv[2], emp, note)
    elif cmd == "sync_checklist":
        if len(sys.argv) < 5:
            print("Error: sync_checklist requires <branch> <title> <employee> [status] [note]")
            sys.exit(1)
        status = sys.argv[5] if len(sys.argv) > 5 else "done"
        note = sys.argv[6] if len(sys.argv) > 6 else ""
        sync_checklist(sys.argv[2], sys.argv[3], sys.argv[4], status, note)
    elif cmd == "get_staff_tasks":
        if len(sys.argv) < 3:
            print("Error: get_staff_tasks requires <employee>")
            sys.exit(1)
        get_staff_tasks(sys.argv[2])
    elif cmd == "onboard_employee":
        if len(sys.argv) < 6:
            print("Error: onboard_employee requires <name> <phone> <email> <branch> [schedule]")
            sys.exit(1)
        sched = sys.argv[6] if len(sys.argv) > 6 else ""
        onboard_employee(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sched)
    elif cmd == "search_employee":
        if len(sys.argv) < 3:
            print("Error: search_employee requires <query>")
            sys.exit(1)
        search_employee(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
