document.addEventListener("DOMContentLoaded", function () {

    function calculateEMI(P, annualRate, months) {
        let r = annualRate / 12 / 100;
        let emi = (P * r * Math.pow(1 + r, months)) /
                  (Math.pow(1 + r, months) - 1);

        let total = emi * months;
        let interest = total - P;

        return { emi, total, interest };
    }

    const amount = document.getElementById("amount");
    const rate = document.getElementById("rate");
    const time = document.getElementById("time");

    const amtVal = document.getElementById("amtVal");
    const rateVal = document.getElementById("rateVal");
    const timeVal = document.getElementById("timeVal");

    const emiText = document.getElementById("emi");
    const totalText = document.getElementById("total");
    const interestText = document.getElementById("interest");

    function update() {
        let P = parseFloat(amount.value) || 0;
        let R = parseFloat(rate.value) || 0;
        let M = parseInt(time.value) || 1;

        amtVal.innerText = P.toLocaleString("en-IN");
        rateVal.innerText = R;
        timeVal.innerText = M;

        let result = calculateEMI(P, R, M);

        emiText.innerText = "EMI: ₹ " + result.emi.toFixed(2);
        totalText.innerText = "Total: ₹ " + result.total.toFixed(2);
        interestText.innerText = "Interest: ₹ " + result.interest.toFixed(2);
    }

    amount.addEventListener("input", update);
    rate.addEventListener("input", update);
    time.addEventListener("input", update);

    update();
});