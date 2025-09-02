from backend.utils_redact import redact_sensitive
from fastapi import APIRouter, Request, HTTPException
from backend.automation import wedge_automation_job, vip_automation_job
from backend.perk_automation import buy_wedge, buy_vip, buy_upload_credit
from backend.config import load_session, save_session
from backend.proxy_config import resolve_proxy_from_session_cfg
from backend.event_log import append_ui_event_log
from datetime import datetime, timezone
import logging

router = APIRouter()

@router.post("/automation/upload_auto")
async def manual_upload_credit(request: Request):
	data = await request.json()
	label = data.get("label")
	amount = data.get("amount", 1)
	if not label:
		raise HTTPException(status_code=400, detail="Session label required.")
	cfg = load_session(label)
	if cfg is None:
		logging.warning(f"[ManualUpload] Session '{label}' not found or not configured.")
		return {"success": False, "error": f"Session '{label}' not found."}
	mam_id = cfg.get('mam', {}).get('mam_id', "")
	from backend.proxy_config import resolve_proxy_from_session_cfg
	proxy_cfg = resolve_proxy_from_session_cfg(cfg)
	now = datetime.now(timezone.utc)
	result = buy_upload_credit(amount, mam_id=mam_id, proxy_cfg=proxy_cfg)
	success = result.get('success', False)
	status_message = f"Purchased {amount}GB Upload Credit" if success else f"Upload Credit purchase failed ({amount}GB)"
	event = {
		"timestamp": now.isoformat(),
		"label": label,
		"event_type": "manual",
		"trigger": "manual",
		"purchase_type": "upload_credit",
		"amount": amount,
		"details": {},
		"result": "success" if success else "failed",
		"error": result.get('error') if not success else None,
		"status_message": status_message
	}
	append_ui_event_log(event)
	try:
		from backend.notifications_backend import notify_event
		if success:
			notify_event(
				event_type="manual_purchase_success",
				label=label,
				status="SUCCESS",
				message=f"Manual Upload Credit purchase succeeded: {amount}GB",
				details={"amount": amount}
			)
		else:
			notify_event(
				event_type="manual_purchase_failure",
				label=label,
				status="FAILED",
				message=f"Manual Upload Credit purchase failed: {amount}GB",
				details={"amount": amount, "error": result.get('error')}
			)
	except Exception:
		...  # Notification failure is ignored
	if success:
		logging.info(f"[ManualUpload] Purchase: {amount}GB upload credit for session '{label}' succeeded.")
	else:
		redacted_result = redact_sensitive(result)
		error_val = redacted_result.get('error') if isinstance(redacted_result, dict) else redacted_result
		logging.warning(f"[ManualUpload] Purchase: {amount}GB upload credit for session '{label}' FAILED. Error: {error_val}")
	return {"success": success, **result}

@router.post("/automation/wedge")
async def manual_wedge(request: Request):
	data = await request.json()
	label = data.get("label")
	method = data.get("method", "points")
	if not label:
		raise HTTPException(status_code=400, detail="Session label required.")
	cfg = load_session(label)
	if cfg is None:
		logging.warning(f"[ManualWedge] Session '{label}' not found or not configured.")
		return {"success": False, "error": f"Session '{label}' not found."}
	mam_id = cfg.get('mam', {}).get('mam_id', "")
	from backend.proxy_config import resolve_proxy_from_session_cfg
	proxy_cfg = resolve_proxy_from_session_cfg(cfg)
	now = datetime.now(timezone.utc)
	result = buy_wedge(mam_id, method=method, proxy_cfg=proxy_cfg)
	success = result.get('success', False)
	status_message = f"Purchased Wedge ({method})" if success else f"Wedge purchase failed ({method})"
	event = {
		"timestamp": now.isoformat(),
		"label": label,
		"event_type": "manual",
		"trigger": "manual",
		"purchase_type": "wedge",
		"amount": 1,
		"details": {"method": method},
		"result": "success" if success else "failed",
		"error": result.get('error') if not success else None,
		"status_message": status_message
	}
	append_ui_event_log(event)
	try:
		from backend.notifications_backend import notify_event
		if success:
			notify_event(
				event_type="manual_purchase_success",
				label=label,
				status="SUCCESS",
				message=f"Manual Wedge purchase succeeded: {method}",
				details={"method": method}
			)
		else:
			notify_event(
				event_type="manual_purchase_failure",
				label=label,
				status="FAILED",
				message=f"Manual Wedge purchase failed: {method}",
				details={"method": method, "error": result.get('error')}
			)
	except Exception:
		...  # Notification failure is ignored
	if success:
		logging.info(f"[ManualWedge] Purchase: Wedge ({method}) for session '{label}' succeeded.")
	else:
		redacted_result = redact_sensitive(result)
		error_val = redacted_result.get('error') if isinstance(redacted_result, dict) else redacted_result
		logging.warning(f"[ManualWedge] Purchase: Wedge ({method}) for session '{label}' FAILED. Error: {error_val}")
	return {"success": success, **result}

@router.post("/automation/vip")
async def manual_vip(request: Request):
	data = await request.json()
	label = data.get("label")
	weeks = data.get("weeks", 4)
	if not label:
		raise HTTPException(status_code=400, detail="Session label required.")
	cfg = load_session(label)
	if cfg is None:
		logging.warning(f"[ManualVIP] Session '{label}' not found or not configured.")
		return {"success": False, "error": f"Session '{label}' not found."}
	mam_id = cfg.get('mam', {}).get('mam_id', "")
	proxy_cfg = resolve_proxy_from_session_cfg(cfg)
	now = datetime.now(timezone.utc)
	is_max = str(weeks).lower() in ["max", "90"]
	if is_max:
		result = buy_vip(mam_id, duration="max", proxy_cfg=proxy_cfg)
		success = result.get('success', False)
		status_message = "Purchased VIP (Max me out!)" if success else "VIP purchase failed (Max me out!)"
		event = {
			"timestamp": now.isoformat(),
			"label": label,
			"event_type": "manual",
			"trigger": "manual",
			"purchase_type": "vip",
			"amount": "max",
			"details": {},
			"result": "success" if success else "failed",
			"error": result.get('error') if not success else None,
			"status_message": status_message
		}
		append_ui_event_log(event)
		try:
			from backend.notifications_backend import notify_event
			if success:
				notify_event(
					event_type="manual_purchase_success",
					label=label,
					status="SUCCESS",
					message="Manual VIP purchase succeeded: Max me out!",
					details={"weeks": "max"}
				)
			else:
				notify_event(
					event_type="manual_purchase_failure",
					label=label,
					status="FAILED",
					message="Manual VIP purchase failed: Max me out!",
					details={"weeks": "max", "error": result.get('error')}
				)
		except Exception:
			...  # Notification failure is ignored
		if success:
			logging.info(f"[ManualVIP] Purchase: VIP (max) for session '{label}' succeeded.")
		else:
			redacted_result = redact_sensitive(result)
			error_val = redacted_result.get('error') if isinstance(redacted_result, dict) else redacted_result
			logging.warning(f"[ManualVIP] Purchase: VIP (max) for session '{label}' FAILED. Error: {error_val}")
		return {"success": success, **result}
	else:
		# For 4 or 8 weeks, just send the value as string
		result = buy_vip(mam_id, duration=str(weeks), proxy_cfg=proxy_cfg)
		success = result.get('success', False)
		status_message = f"Purchased VIP ({weeks} weeks)" if success else f"VIP purchase failed ({weeks} weeks)"
		event = {
			"timestamp": now.isoformat(),
			"label": label,
			"event_type": "manual",
			"trigger": "manual",
			"purchase_type": "vip",
			"amount": weeks,
			"details": {},
			"result": "success" if success else "failed",
			"error": result.get('error') if not success else None,
			"status_message": status_message
		}
		append_ui_event_log(event)
		try:
			from backend.notifications_backend import notify_event
			if success:
				notify_event(
					event_type="manual_purchase_success",
					label=label,
					status="SUCCESS",
					message=f"Manual VIP purchase succeeded: {weeks} weeks",
					details={"weeks": weeks}
				)
			else:
				notify_event(
					event_type="manual_purchase_failure",
					label=label,
					status="FAILED",
					message=f"Manual VIP purchase failed: {weeks} weeks",
					details={"weeks": weeks, "error": result.get('error')}
				)
		except Exception:
			...  # Notification failure is ignored
		if success:
			logging.info(f"[ManualVIP] Purchase: VIP ({weeks} weeks) for session '{label}' succeeded.")
		else:
			redacted_result = redact_sensitive(result)
			error_val = redacted_result.get('error') if isinstance(redacted_result, dict) else redacted_result
			logging.warning(f"[ManualVIP] Purchase: VIP ({weeks} weeks) for session '{label}' FAILED. Error: {error_val}")
		return {"success": success, **result}
