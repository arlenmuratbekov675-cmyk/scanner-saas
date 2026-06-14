"""
RCP-2 Execution - 20 leads, PAIN message, Kyrgyzstan.
Tracks: volume, funnel, intent classification, stability.
"""
import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("C:/Projects/mimo/agency/engine/data/rcp1")

LEADS_FILE = DATA_DIR / "leads.json"
SENT_FILE = DATA_DIR / "sent_log.json"
RESPONSE_FILE = DATA_DIR / "responses.json"
REPORT_FILE = DATA_DIR / "rcp2_report.json"


class RCP2Execution:

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def load_leads(self):
        return json.loads(LEADS_FILE.read_text(encoding="utf-8"))

    def get_status(self):
        leads = self.load_leads()
        sent = json.loads(SENT_FILE.read_text(encoding="utf-8"))
        responses = json.loads(RESPONSE_FILE.read_text(encoding="utf-8"))

        total = len(leads)
        conn_sent = len([x for x in sent if x["action"] == "connection_sent"])
        conn_accepted = len([x for x in sent if x["action"] == "connection_accepted"])
        msg_sent = len([x for x in sent if x["action"] == "message_sent"])
        total_replies = len(responses)

        # Intent classification
        high_intent = len([r for r in responses if r.get("intent") == "high"])
        medium_intent = len([r for r in responses if r.get("intent") == "medium"])
        low_intent = len([r for r in responses if r.get("intent") == "low"])

        accept_rate = (conn_accepted / conn_sent * 100) if conn_sent > 0 else 0
        reply_rate = (total_replies / msg_sent * 100) if msg_sent > 0 else 0
        high_rate = (high_intent / total_replies * 100) if total_replies > 0 else 0

        return {
            "total_leads": total,
            "connection_sent": conn_sent,
            "connection_accepted": conn_accepted,
            "message_sent": msg_sent,
            "total_replies": total_replies,
            "accept_rate": round(accept_rate, 1),
            "reply_rate": round(reply_rate, 1),
            "intent": {
                "high": high_intent,
                "medium": medium_intent,
                "low": low_intent,
                "high_rate": round(high_rate, 1),
            },
            "responses": responses,
        }

    def print_status(self):
        s = self.get_status()

        print("=" * 60)
        print("RCP-2 STATUS")
        print("=" * 60)
        print(f"Leads: {s['total_leads']}")
        print(f"Connection sent: {s['connection_sent']}")
        print(f"Connection accepted: {s['connection_accepted']} ({s['accept_rate']}%)")
        print(f"Message sent: {s['message_sent']}")
        print(f"Replies: {s['total_replies']} ({s['reply_rate']}%)")
        print(f"\nIntent breakdown:")
        print(f"  HIGH:   {s['intent']['high']}")
        print(f"  MEDIUM: {s['intent']['medium']}")
        print(f"  LOW:    {s['intent']['low']}")
        print(f"  HIGH%:  {s['intent']['high_rate']}%")

        if s["responses"]:
            print(f"\nResponses:")
            for r in s["responses"]:
                print(f"  - {r['lead_name']}: {r['response_type']} (intent: {r.get('intent', 'unknown')})")

    def generate_report(self, predicted_reply_rate=7.5):
        s = self.get_status()

        reply_error = abs(predicted_reply_rate - s["reply_rate"])

        # Determine stability (needs more data)
        stable = s["total_replies"] >= 10

        # Determine calibration
        if reply_error < 3:
            calibration = "CALIBRATED"
        elif reply_error < 7:
            calibration = "NEAR CALIBRATED"
        elif reply_error < 15:
            calibration = "UNCALIBRATED"
        else:
            calibration = "POORLY CALIBRATED"

        # Funnel collapse point
        if s["connection_sent"] > 0:
            accept_to_reply = s["total_replies"] / s["connection_sent"] * 100
        else:
            accept_to_reply = 0

        report = {
            "rcp_version": "RCP-2",
            "country": "Kyrgyzstan",
            "message_style": "PAIN",
            "sample_size": s["total_leads"],
            "predicted_reply_rate": predicted_reply_rate,
            "actual_reply_rate": s["reply_rate"],
            "reply_error": round(reply_error, 1),
            "calibration": calibration,
            "stable": stable,
            "funnel": {
                "sent": s["connection_sent"],
                "accepted": s["connection_accepted"],
                "messaged": s["message_sent"],
                "replied": s["total_replies"],
                "accept_rate": s["accept_rate"],
                "reply_rate": s["reply_rate"],
                "accept_to_reply": round(accept_to_reply, 1),
            },
            "intent_distribution": s["intent"],
            "verdict": self._get_verdict(s, reply_error),
            "timestamp": datetime.utcnow().isoformat(),
        }

        REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report

    def _get_verdict(self, s, error):
        if s["total_replies"] < 5:
            return "INSUFFICIENT DATA - Need more responses"
        elif error < 5 and s["intent"]["high"] > 0:
            return "SIGNAL DETECTED - Model partially validated"
        elif error < 10:
            return "WEAK SIGNAL - Model needs adjustment"
        else:
            return "NOISE - Model not validated"


def run_rcp2():
    exec_layer = RCP2Execution()
    exec_layer.print_status()

    report = exec_layer.generate_report()

    print(f"\n{'=' * 60}")
    print("RCP-2 REPORT")
    print("=" * 60)
    print(f"Predicted: {report['predicted_reply_rate']}%")
    print(f"Actual: {report['actual_reply_rate']}%")
    print(f"Error: {report['reply_error']}%")
    print(f"Calibration: {report['calibration']}")
    print(f"Stable: {report['stable']}")
    print(f"Verdict: {report['verdict']}")
    print(f"\nIntent: HIGH={report['intent_distribution']['high']} | MEDIUM={report['intent_distribution']['medium']} | LOW={report['intent_distribution']['low']}")


if __name__ == "__main__":
    run_rcp2()
