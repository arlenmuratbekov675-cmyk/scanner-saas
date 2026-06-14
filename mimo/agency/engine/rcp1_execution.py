"""
RCP-1 Execution Layer - Minimal, clean implementation.
Controlled experiment: 10 leads, 1 message style, no noise.
"""
import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("C:/Projects/mimo/agency/engine/data/rcp1")

LEADS_FILE = DATA_DIR / "leads.json"
SENT_FILE = DATA_DIR / "sent_log.json"
RESPONSE_FILE = DATA_DIR / "responses.json"
REPORT_FILE = DATA_DIR / "final_report.json"


class RCP1ExecutionLayer:

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._init_files()

    def _init_files(self):
        for file in [LEADS_FILE, SENT_FILE, RESPONSE_FILE, REPORT_FILE]:
            if not file.exists():
                file.write_text("[]", encoding="utf-8")

    # ---------------------------
    # LOAD LEADS
    # ---------------------------
    def load_leads(self):
        return json.loads(LEADS_FILE.read_text())

    def save_leads(self, leads):
        LEADS_FILE.write_text(json.dumps(leads, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------------------------
    # EXPORT FOR EXECUTION
    # ---------------------------
    def export_queue(self, leads, message_generator):
        """
        Prepare 10 leads for outreach
        """
        queue = []

        for lead in leads[:10]:
            msg = message_generator.generate_for_lead(lead)

            if msg:
                queue.append({
                    "lead_name": lead.clinic.name,
                    "country": lead.clinic.country,
                    "tier": lead.tier.value,
                    "score": lead.total_score,
                    "connection_request": msg.connection_request,
                    "first_message": msg.first_message,
                    "status": "pending"
                })

        self.save_leads(queue)
        return queue

    # ---------------------------
    # LOG SENT
    # ---------------------------
    def log_sent(self, lead_name, action):
        data = json.loads(SENT_FILE.read_text())

        data.append({
            "lead_name": lead_name,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        })

        SENT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------------------------
    # LOG RESPONSE
    # ---------------------------
    def log_response(self, lead_name, response_type):
        """
        response_type: positive / neutral / negative / no_response
        """
        data = json.loads(RESPONSE_FILE.read_text())

        data.append({
            "lead_name": lead_name,
            "response_type": response_type,
            "timestamp": datetime.utcnow().isoformat()
        })

        RESPONSE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------------------------
    # REPORT
    # ---------------------------
    def generate_report(self, predicted_reply_rate=7.5):
        sent = json.loads(SENT_FILE.read_text())
        responses = json.loads(RESPONSE_FILE.read_text())

        total_sent = len([x for x in sent if x["action"] == "connection_sent"])
        total_accepted = len([x for x in sent if x["action"] == "connection_accepted"])
        total_responses = len(responses)
        positive_responses = len([r for r in responses if r["response_type"] == "positive"])

        accept_rate = (total_accepted / total_sent * 100) if total_sent > 0 else 0
        reply_rate = (total_responses / total_sent * 100) if total_sent > 0 else 0
        positive_rate = (positive_responses / total_sent * 100) if total_sent > 0 else 0

        # Calibration
        reply_error = abs(predicted_reply_rate - reply_rate)
        calibrated = reply_error < 5.0  # Within 5% = calibrated

        report = {
            "predicted_reply_rate": predicted_reply_rate,
            "actual_reply_rate": round(reply_rate, 2),
            "reply_error": round(reply_error, 2),
            "calibrated": calibrated,
            "metrics": {
                "total_sent": total_sent,
                "total_accepted": total_accepted,
                "total_responses": total_responses,
                "positive_responses": positive_responses,
                "accept_rate": round(accept_rate, 2),
                "reply_rate": round(reply_rate, 2),
                "positive_rate": round(positive_rate, 2),
            },
            "verdict": self._get_verdict(reply_error),
            "timestamp": datetime.utcnow().isoformat()
        }

        REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        return report

    def _get_verdict(self, error):
        if error < 3:
            return "CALIBRATED - Model is accurate"
        elif error < 7:
            return "NEAR CALIBRATED - Minor adjustment needed"
        elif error < 15:
            return "UNCALIBRATED - Significant correction needed"
        else:
            return "POORLY CALIBRATED - Model needs major revision"

    # ---------------------------
    # PRINT STATUS
    # ---------------------------
    def print_status(self):
        leads = self.load_leads()
        sent = json.loads(SENT_FILE.read_text())
        responses = json.loads(RESPONSE_FILE.read_text())

        print("=" * 60)
        print("RCP-1 EXECUTION STATUS")
        print("=" * 60)
        print(f"Leads loaded: {len(leads)}")
        print(f"Connection requests sent: {len([x for x in sent if x['action'] == 'connection_sent'])}")
        print(f"Connections accepted: {len([x for x in sent if x['action'] == 'connection_accepted'])}")
        print(f"Messages sent: {len([x for x in sent if x['action'] == 'message_sent'])}")
        print(f"Responses received: {len(responses)}")

        if responses:
            print("\nResponses:")
            for r in responses:
                print(f"  - {r['lead_name']}: {r['response_type']}")


def demo_rcp1():
    """Demo the RCP-1 execution layer."""
    import sys
    sys.path.insert(0, "C:/Projects/mimo/agency/engine")

    from rcp1_calibration import RealityCalibrationProtocol
    from message_generator import MessageGeneratorV2

    # Initialize
    rcp = RealityCalibrationProtocol()
    msg_gen = MessageGeneratorV2()
    execution = RCP1ExecutionLayer()

    # Score leads
    scored_leads = rcp.score_leads()

    # Export queue
    queue = execution.export_queue(scored_leads, msg_gen)

    print("=" * 60)
    print("RCP-1 EXECUTION LAYER READY")
    print("=" * 60)
    print(f"\nExported {len(queue)} leads to: {LEADS_FILE}")

    # Show first lead
    if queue:
        lead = queue[0]
        name = lead['lead_name'].encode('ascii', 'replace').decode('ascii')
        cr = lead['connection_request'].encode('ascii', 'replace').decode('ascii')
        fm = lead['first_message'].encode('ascii', 'replace').decode('ascii')
        print(f"\nFirst lead: {name}")
        print(f"Tier: {lead['tier']}")
        print(f"Score: {lead['score']}")
        print(f"\nConnection Request:")
        print(cr)
        print(f"\nFirst Message:")
        print(fm)

    print(f"\n{'=' * 60}")
    print("NEXT STEPS:")
    print("1. Send 10 connection requests (copy from leads.json)")
    print("2. Log: engine.log_sent('Clinic Name', 'connection_sent')")
    print("3. When accepted: engine.log_sent('Clinic Name', 'connection_accepted')")
    print("4. Send first message: engine.log_sent('Clinic Name', 'message_sent')")
    print("5. Log reply: engine.log_response('Clinic Name', 'positive')")
    print("6. Get report: engine.generate_report()")
    print("=" * 60)


if __name__ == "__main__":
    demo_rcp1()
