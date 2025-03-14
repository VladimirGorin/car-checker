const APIUrl = "http://localhost:8001/api";

function showError(message) {
    let alertBox = document.getElementById("alert-box");
    if (!alertBox) {
        alertBox = document.createElement("div");
        alertBox.id = "alert-box";
        alertBox.className = "alert alert-danger position-fixed top-0 end-0 m-3 shadow";
        alertBox.style.zIndex = "1050";
        document.body.appendChild(alertBox);
    }
    alertBox.innerText = message;
    alertBox.classList.remove("d-none");
    setTimeout(() => alertBox.classList.add("d-none"), 5000);
}

function updateCarInfo(data, isReady) {
    const infoBox = document.getElementById("car-info");

    const brandLogo = document.getElementById("car-logo");
    const carTitle = document.getElementById("car-title");
    const reportDate = document.getElementById("report-date");
    const plateNumberElem = document.getElementById("plate-number");
    const yearElem = document.getElementById("year");
    const steeringElem = document.getElementById("steering");
    const powerElem = document.getElementById("power");
    const vinElem = document.getElementById("result-vin");
    const bodyNumberElem = document.getElementById("body-number");
    const categoryElem = document.getElementById("category");
    const engineElem = document.getElementById("engine");
    const volumeElem = document.getElementById("volume");

    const getMoreElem = document.getElementById("get-more-car-info");
    const pdfElem = document.getElementById("car-pdf-info");

    if (data?.tech_data?.brand?.logotype?.uri) {
        brandLogo.src = data.tech_data.brand.logotype.uri;
    } else {
        brandLogo.src = "car-logo-placeholder.png"; // Путь к изображению-заглушке
    }

    carTitle.innerText = `${data?.tech_data?.brand?.name?.original || ""}
                          ${data?.tech_data?.model?.name?.original || ""},
                          ${data?.tech_data?.year || "Год неизвестен"}`;

    reportDate.innerText = new Date().toLocaleDateString();
    plateNumberElem.innerText = data?.identifiers?.vehicle?.reg_num || "Отсутствует";
    yearElem.innerText = data?.tech_data?.year || "Нет данных";

    steeringElem.innerText = data?.tech_data?.wheel?.position
        ? (data.tech_data.wheel.position === "LEFT" ? "Левый руль" : "Правый руль")
        : "Нет данных";

    powerElem.innerText = data?.tech_data?.engine?.power?.hp ? `${data.tech_data.engine.power.hp} л.с.` : "Нет данных";
    vinElem.innerText = data?.identifiers?.vehicle?.vin || "Нет VIN";
    bodyNumberElem.innerText = data?.identifiers?.vehicle?.body || "Нет VIN";

    categoryElem.innerText = data?.additional_info?.vehicle?.category?.code
        ? `«${data.additional_info.vehicle.category.code}»`
        : "Нет данных";

    engineElem.innerText = data?.tech_data?.engine?.fuel?.type || "Нет данных";
    volumeElem.innerText = data?.tech_data?.engine?.volume ? `${data.tech_data.engine.volume} куб. см` : "Нет данных";

    if (isReady) {
        getMoreElem.classList.add("d-none");
        pdfElem.classList.remove("d-none");
    } else {
        getMoreElem.classList.remove("d-none");
        pdfElem.classList.add("d-none");
    }

    infoBox.classList.remove("d-none");
}

async function checkCar(subscription) {
    const loadingElement = document.getElementById("loading");
    loadingElement.classList.remove("d-none");

    let vinInput = document.getElementById("vin");
    let regNumberInput = document.getElementById("regNumber");
    let bodyNumberInput = document.getElementById("bodyNumber");

    let vinValue = vinInput.value.trim();
    let regNumberValue = regNumberInput.value.trim();
    let bodyNumberValue = bodyNumberInput.value.trim();

    if (!vinValue && !regNumberValue && !bodyNumberValue) {
        showError("Введите VIN госномер или кузов перед проверкой!");
        loadingElement.classList.add("d-none");
        return;
    }

    let carType = "VIN";
    let carQuery = vinValue;

    if (vinValue.length) {
        carType = "VIN"
        carQuery = vinValue
    } else if (regNumberValue.length) {
        carType = "GRZ"
        carQuery = regNumberValue
    } else if (bodyNumberValue.length) {
        carType = "BODY"
        carQuery = bodyNumberValue
    }


    const reportUuid = localStorage.getItem("requestUuid");
    // console.log("reportUuid", reportUuid);

    const requestBody = JSON.stringify({
        query: carQuery,
        car_type: carType,
        subscription,
        report_uuid: subscription ? reportUuid : ""
    });

    // console.log("requestBody", requestBody);

    try {
        const response = await fetch(`${APIUrl}/car/info`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: requestBody
        });

        if (!response.ok) {
            throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        const carInfo = data?.content?.message?.content?.content;
        const requestUuid = data?.content?.message?.uuid;
        const isReportFull = data?.content?.message?.is_ready && subscription



        // console.log("isReportFull", isReportFull);
        // console.log("subscription", subscription);

        if (carInfo) {
            // await createPDF(data?.content?.message, requestUuid)

            if (isReportFull) {
                await createPDF(data?.content?.message, requestUuid)
            }

            updateCarInfo(carInfo, isReportFull);

            vinInput.value = "";
            regNumberInput.value = "";
            bodyNumberInput.value = "";

            localStorage.setItem("carType", carType);
            localStorage.setItem("carQuery", carQuery);
            localStorage.setItem("requestUuid", requestUuid);

            if (subscription) {
                localStorage.removeItem("paymentId")
            }
        } else {
            showError("Автомобиль не найден.");
        }
    } catch (error) {
        showError("Ошибка запроса: " + error.message);
    } finally {
        loadingElement.classList.add("d-none");
    }
}

async function createPayment() {
    const loadingElement = document.getElementById("loading");
    loadingElement.classList.remove("d-none");

    const requestBody = JSON.stringify({
        amount: 89.00,
    });

    fetch(`${APIUrl}/payment/create`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: requestBody
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            const paymentURL = data?.message?.confirmation?.confirmation_url;
            const paymentID = data?.message?.id
            // console.log("paymentURL:", paymentURL);
            // console.log("Ответ сервера:", data);

            if (paymentURL) {
                localStorage.setItem("paymentId", paymentID)

                window.location.href = paymentURL
            } else {
                showError("Не удалось получить ссылку на оплату.");
            }

        })
        .catch(error => {
            showError("Ошибка запроса: " + error.message);
        })
        .finally(() => {
            loadingElement.classList.add("d-none");
        });
}

async function createPDF(json, reportUuid) {
    const loadingElement = document.getElementById("loading");
    loadingElement.classList.remove("d-none");

    try {
        const requestBody = JSON.stringify({
            "data": { result: json },
            "report_uuid": reportUuid
        });

        const response = await fetch(`${APIUrl}/car/create-pdf`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: requestBody
        });

        if (!response.ok) {
            throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        // console.log("Ответ сервера:", data);

        const pdfPATH = data?.message;
        const pdfURL = `${APIUrl}/files/${pdfPATH}`
        if (pdfURL) {
            // localStorage.setItem("pdfURL", pdfURL);
            const pdfLink = document.getElementById("car-pdf-info");

            if (pdfURL) {
                pdfLink.href = pdfURL;
            }
        } else {
            showError("Не удалось получить ссылку на PDF файл.");
        }
    } catch (error) {
        showError("Ошибка запроса: " + error.message);
    } finally {
        loadingElement.classList.add("d-none");
    }
}


document.addEventListener("DOMContentLoaded", function () {
    const paymentId = localStorage.getItem("paymentId")

    if (!paymentId) {
        return
    }

    const loadingElement = document.getElementById("loading");
    loadingElement.classList.remove("d-none");

    const requestBody = JSON.stringify({
        payment_id: paymentId,
    });


    fetch(`${APIUrl}/payment/get`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: requestBody
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(async (data) => {
            const paymentPaid = data?.message?.paid
            // const paymentPaid = true

            // console.log("paymentPaid:", paymentPaid);
            // console.log("Ответ сервера:", data);

            if (paymentPaid) {
                const carType = localStorage.getItem("carType")
                const carQuery = localStorage.getItem("carQuery")

                let vinInput = document.getElementById("vin");
                let regNumberInput = document.getElementById("regNumber");
                let bodyNumberInput = document.getElementById("bodyNumber");

                if (carType === "VIN") {
                    vinInput.value = carQuery
                } else if (carType === "GRZ") {
                    regNumberInput.value = carQuery
                } else if (carType === "BODY") {
                    bodyNumberInput.value = carQuery
                } else {
                    showError("Ошибка, не удалось получить тип элемента.");
                    return
                }

                await checkCar(true)
            } else {
                // showError("Отчет не был сгенерирован, так как вы не оплатили полный отчет.");
                console.error("Отчет не был сгенерирован, так как вы не оплатили полный отчет.")
                return
            }
        })
        .catch(error => {
            showError("Ошибка запроса: " + error.message);
        })
        .finally(() => {
            loadingElement.classList.add("d-none");
        });
});
