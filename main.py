from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import Counter

from app.bedrock_agent import ask_nova
from app.aws_services import get_ec2_instances, get_s3_buckets

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "application": "CloudOps AI Agent",
        "model": "Amazon Nova Lite"
    })


def get_inventory_answer(question, ec2_instances, s3_buckets):
    q = question.lower()

    # Exact S3 inventory questions
    s3_keywords = ["bucket", "buckets", "s3"]
    inventory_keywords = [
        "how many", "count", "total", "list",
        "show", "display", "available", "inventory"
    ]

    if (
        any(word in q for word in s3_keywords)
        and any(word in q for word in inventory_keywords)
    ):
        total = len(s3_buckets)
        regions = Counter(bucket["Region"] for bucket in s3_buckets)

        lines = [
            f"Your AWS account currently has {total} S3 buckets.",
            "",
            "BUCKET COUNT BY REGION:"
        ]

        for region, count in sorted(regions.items()):
            lines.append(f"- {region}: {count} buckets")

        lines.extend([
            "",
            "COMPLETE S3 BUCKET INVENTORY:"
        ])

        for index, bucket in enumerate(s3_buckets, 1):
            lines.append(
                f"{index}. {bucket['BucketName']} "
                f"| Region: {bucket['Region']} "
                f"| Created: {bucket['CreationDate']}"
            )

        return "\n".join(lines), {
            "type": "s3_inventory",
            "total_buckets": total,
            "regional_counts": dict(regions)
        }

    # Exact EC2 inventory questions
    ec2_keywords = ["ec2", "instance", "instances"]

    if (
        any(word in q for word in ec2_keywords)
        and any(word in q for word in inventory_keywords)
    ):
        total = len(ec2_instances)
        states = Counter(
            instance["State"] for instance in ec2_instances
        )

        lines = [
            f"Your AWS region currently has {total} EC2 instances.",
            "",
            "INSTANCE COUNTS BY STATE:"
        ]

        for state, count in sorted(states.items()):
            lines.append(f"- {state}: {count}")

        lines.extend([
            "",
            "COMPLETE EC2 INVENTORY:"
        ])

        for index, instance in enumerate(ec2_instances, 1):
            lines.append(
                f"{index}. {instance['InstanceId']} "
                f"| State: {instance['State']} "
                f"| Type: {instance['InstanceType']} "
                f"| Private IP: {instance['PrivateIp']}"
            )

        return "\n".join(lines), {
            "type": "ec2_inventory",
            "total_instances": total,
            "state_counts": dict(states)
        }

    return None, None


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        ec2_instances = get_ec2_instances()
        s3_buckets = get_s3_buckets()

        # Handle exact inventory questions using Python
        answer, inventory = get_inventory_answer(
            question,
            ec2_instances,
            s3_buckets
        )

        if answer is not None:
            return jsonify({
                "answer": answer,
                "source": "python_live_inventory",
                "inventory": inventory
            })

        # General questions go to Amazon Nova Lite
        context = f"""
You are a CloudOps AI Assistant.

Use this live AWS inventory to answer the user.

EC2 INVENTORY:
{ec2_instances}

S3 BUCKET INVENTORY:
{s3_buckets}

Rules:
- Never invent AWS resource IDs or names.
- Do not claim an inventory count unless it is calculated
  from the supplied data.
- For exact counts and complete listings, Python handles
  the response separately.
- Explain AWS concepts clearly.
- Give practical troubleshooting steps.
"""

        answer = ask_nova(
            context + "\nUSER QUESTION:\n" + question
        )

        return jsonify({
            "answer": answer,
            "source": "amazon_nova_lite"
        })

    except Exception:
        app.logger.exception("Chat request failed")
        return jsonify({
            "error": "Unable to process request"
        }), 500


@app.route("/ec2", methods=["GET"])
def ec2():
    try:
        instances = get_ec2_instances()
        return jsonify({
            "total": len(instances),
            "instances": instances
        })
    except Exception:
        app.logger.exception("EC2 request failed")
        return jsonify({
            "error": "Unable to retrieve EC2 instances"
        }), 500


@app.route("/s3", methods=["GET"])
def s3():
    try:
        buckets = get_s3_buckets()
        regions = Counter(
            bucket["Region"] for bucket in buckets
        )

        return jsonify({
            "total": len(buckets),
            "regional_counts": dict(regions),
            "buckets": buckets
        })
    except Exception:
        app.logger.exception("S3 request failed")
        return jsonify({
            "error": "Unable to retrieve S3 buckets"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
