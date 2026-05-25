# ml-engine/services/insight_generator.py

HINDI_TRANSLATIONS = {
    "Food": "खाना",
    "Transport": "यातायात",
    "Groceries": "किराना",
    "Rent": "किराया",
    "EMI": "ईएमआई",
    "Shopping": "खरीदारी",
    "Investments": "निवेश",
    "Other": "अन्य",
}

def generate_insights(summary: dict, language: str = "en") -> list[dict]:
    """Generate 3-5 plain language insights from spending summary."""
    insights = []
    by_cat = summary.get("by_category", {})
    total = summary.get("total_debit", 0)
    if total == 0:
        return []

    # Sort categories by amount
    sorted_cats = sorted(by_cat.items(), key=lambda x: x[1]["amount"], reverse=True)

    for category, data in sorted_cats[:3]:
        pct = data["percentage"]
        amount = data["amount"]
        count = data["transaction_count"]

        if category == "Food" and pct > 30:
            en_body = (
                f"You spent ₹{amount:,.0f} on food this month ({pct:.0f}% of total). "
                f"That's across {count} transactions. Consider meal prepping to cut this by 20%."
            )
            hi_body = (
                f"इस महीने आपने खाने पर ₹{amount:,.0f} खर्च किए (कुल का {pct:.0f}%). "
                f"यह {count} लेनदेन में था. घर पर खाना बनाने से 20% बचत हो सकती है."
            )
            insights.append({
                "type": "overspend",
                "category": category,
                "title_en": "Food spending is high",
                "body_en": en_body,
                "title_hi": "खाने पर ज़्यादा खर्च",
                "body_hi": hi_body,
                "severity": "warning",
            })

        elif category == "Investments" and pct >= 10:
            en_body = (
                f"You invested ₹{amount:,.0f} this month ({pct:.0f}% of income). "
                f"That's above the recommended 10% - excellent financial habit."
            )
            hi_body = (
                f"इस महीने आपने ₹{amount:,.0f} निवेश किए ({pct:.0f}%). "
                f"यह अनुशंसित 10% से अधिक है - बहुत अच्छी आदत."
            )
            insights.append({
                "type": "positive",
                "category": category,
                "title_en": "Great savings habit",
                "body_en": en_body,
                "title_hi": "बेहतरीन बचत की आदत",
                "body_hi": hi_body,
                "severity": "success",
            })

        elif category == "Transport" and pct > 15:
            en_body = (
                f"Transport costs are ₹{amount:,.0f} ({pct:.0f}%). "
                f"Consider monthly metro/bus pass or carpooling to reduce this."
            )
            hi_body = (
                f"यातायात पर ₹{amount:,.0f} ({pct:.0f}%) खर्च हुए. "
                f"मेट्रो पास या कारपूल से खर्च कम हो सकता है."
            )
            insights.append({
                "type": "suggestion",
                "category": category,
                "title_en": "High transport costs",
                "body_en": en_body,
                "title_hi": "यातायात पर ज़्यादा खर्च",
                "body_hi": hi_body,
                "severity": "warning",
            })

        elif category == "Rent" and pct > 20:
            en_body = (
                f"Housing costs are ₹{amount:,.0f} this month ({pct:.0f}% of spending). "
                f"That is your largest fixed expense in this statement."
            )
            hi_body = (
                f"इस महीने आपने किराये पर ₹{amount:,.0f} खर्च किए (कुल खर्च का {pct:.0f}%)। "
                f"यह इस स्टेटमेंट में सबसे बड़ा निश्चित खर्च है।"
            )
            insights.append({
                "type": "overspend",
                "category": category,
                "title_en": "Rent is your biggest expense",
                "body_en": en_body,
                "title_hi": "किराया सबसे बड़ा खर्च है",
                "body_hi": hi_body,
                "severity": "warning",
            })

        elif category == "Shopping" and pct > 15:
            en_body = (
                f"Shopping spend is ₹{amount:,.0f} ({pct:.0f}% of total) across {count} purchases. "
                f"Review large one-time orders to avoid impulse buys."
            )
            hi_body = (
                f"खरीदारी पर ₹{amount:,.0f} ({pct:.0f}%) खर्च हुआ, {count} खरीदारी में। "
                f"बड़े एकमुश्त ऑर्डर की समीक्षा करें।"
            )
            insights.append({
                "type": "suggestion",
                "category": category,
                "title_en": "Shopping spend is elevated",
                "body_en": en_body,
                "title_hi": "खरीदारी खर्च अधिक है",
                "body_hi": hi_body,
                "severity": "warning",
            })

        elif category == "EMI" and pct >= 10:
            en_body = (
                f"Loan EMIs total ₹{amount:,.0f} ({pct:.0f}% of spending) across {count} payments. "
                f"Track due dates to avoid late fees."
            )
            hi_body = (
                f"लोन ईएमआई कुल ₹{amount:,.0f} ({pct:.0f}%) हैं, {count} भुगतानों में। "
                f"देरी शुल्क से बचने के लिए तारीखें याद रखें।"
            )
            insights.append({
                "type": "suggestion",
                "category": category,
                "title_en": "EMI payments add up",
                "body_en": en_body,
                "title_hi": "ईएमआई भुगतान जुड़ते हैं",
                "body_hi": hi_body,
                "severity": "info",
            })

    # Add anomaly insight if anomalies detected
    anomalies = summary.get("anomalies", [])
    if anomalies:
        a = anomalies[0]
        insights.append({
            "type": "anomaly",
            "category": a.get("category", "Other"),
            "title_en": "Unusual transaction detected",
            "body_en": f"Your {a['merchant']} payment of ₹{a['amount']:,.0f} is unusually high. {a['reason']}",
            "title_hi": "असामान्य लेनदेन मिला",
            "body_hi": f"₹{a['amount']:,.0f} का {a['merchant']} भुगतान असामान्य रूप से अधिक है.",
            "severity": "error",
        })

    # Return based on requested language
    return [
        {
            "type": i["type"],
            "category": i["category"],
            "title": i[f"title_{language}"] or i["title_en"],
            "body": i[f"body_{language}"] or i["body_en"],
            "severity": i["severity"],
        }
        for i in insights
    ]
