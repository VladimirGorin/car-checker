const APIUrl = "https://avinfoheck.ru/api";

// https://avinfoheck.ru/api
// http://localhost:8001/api


function showError(message) {
    try {
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
    } catch (error) {
        alert(`Ошибка в showError: ${error}`);
    }
}

function scrollToBottom(speed = "smooth") {
    try {
        window.scrollTo({ top: document.body.scrollHeight, behavior: speed });
    } catch (error) {
        showError("Ошибка при прокрутке страницы: " + error);
    }
}

function sendNotification(text) {
    try {
        if (Notification.permission === "granted") {
            navigator.serviceWorker.getRegistration().then(registration => {
                try {
                    if (registration) {
                        registration.showNotification(text, {
                            body: text,
                            icon: "/favicon-16x16.png"
                        });
                    } else {
                        showError("Service Worker не зарегистрирован");
                    }
                } catch (error) {
                    showError("Ошибка при показе уведомления: " + error);
                }
            });
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(permission => {
                try {
                    if (permission === "granted") {
                        sendNotification(text);
                    }
                } catch (error) {
                    showError("Ошибка при запросе разрешения на уведомления: " + error);
                }
            });
        }
    } catch (error) {
        showError("Ошибка при отправке уведомления: " + error);
    }
}

function getUserId() {
    try {
        return localStorage.getItem("userId");
    } catch (error) {
        showError("Ошибка при получении userId: " + error);
        return null;
    }
}
function updateCarInfo(data, isReady, pdfURL) {
    try {
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
            brandLogo.src = "car-logo-placeholder.png";
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

        console.log("pdfURL", pdfURL)
        pdfElem.href = pdfURL

        if (isReady) {
            getMoreElem.classList.add("d-none");
            pdfElem.classList.remove("d-none");
        } else {
            getMoreElem.classList.remove("d-none");
            pdfElem.classList.add("d-none");
        }

        infoBox.classList.remove("d-none");

        scrollToBottom()
    } catch (error) {
        showError("Ошибка при обновлении информации о машине: " + error);
    }
}

async function checkCar(subscription) {
    try {
        const loadingElement = document.getElementById("loading");
        loadingElement.classList.remove("d-none");

        let vinInput = document.getElementById("vin");
        let regNumberInput = document.getElementById("regNumber");
        let bodyNumberInput = document.getElementById("bodyNumber");

        let vinValue = vinInput.value.trim();
        let regNumberValue = regNumberInput.value.trim();
        let bodyNumberValue = bodyNumberInput.value.trim();

        function isValidVin(vin) {
            return /^[A-HJ-NPR-Z0-9]{17}$/i.test(vin.toLowerCase());
        }

        function isValidRegNumber(regNumber) {
            return /^[А-ЯЁA-Z]{1,2}\d{3}[А-ЯЁA-Z]{2,3}\d{2,3}$/i.test(regNumber.toLowerCase());
        }

        function isValidBodyNumber(bodyNumber) {
            return /^[A-Za-z0-9-]{6,}$/i.test(bodyNumber.toLowerCase());
        }

        if (!vinValue && !regNumberValue && !bodyNumberValue) {
            showError("Введите VIN, госномер или номер кузова перед проверкой!");
            loadingElement.classList.add("d-none");
            return;
        }

        let carType = "";
        let carQuery = "";

        if (vinValue.length) {
            if (!isValidVin(vinValue)) {
                showError("Неверный формат VIN.");
                loadingElement.classList.add("d-none");
                return;
            }
            carType = "VIN";
            carQuery = vinValue;
        } else if (regNumberValue.length) {
            if (!isValidRegNumber(regNumberValue)) {
                showError("Неверный формат госномера.");
                loadingElement.classList.add("d-none");
                return;
            }
            carType = "GRZ";
            carQuery = regNumberValue;
        } else if (bodyNumberValue.length) {
            if (!isValidBodyNumber(bodyNumberValue)) {
                showError("Неверный формат номера кузова.");
                loadingElement.classList.add("d-none");
                return;
            }
            carType = "BODY";
            carQuery = bodyNumberValue;
        }

        const reportUuid = localStorage.getItem("requestUuid");

        const requestBody = JSON.stringify({
            query: carQuery,
            car_type: carType,
            subscription,
            report_uuid: subscription ? reportUuid : "",
            user_id: getUserId()
        });

        const response = await fetch(`${APIUrl}/car/info`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: requestBody
        });

        if (!response.ok) {
            let errorMessage = "Произошла ошибка";

            try {
                const data = await response.json();
                if (data.detail) {
                    errorMessage = data.detail;
                }
            } catch (e) {
                errorMessage = `Ошибка: ${response.status}`;
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();
        const carInfo = data?.content?.message?.content?.content;
        const requestUuid = data?.content?.message?.uuid;
        const isReportFull = data?.content?.message?.is_ready && subscription;

        if (carInfo) {
            let pdfReportURL = "#"

            if (isReportFull) {
                pdfReportURL = `${APIUrl}/files/${data?.content?.pdf_url}`
            }

            updateCarInfo(carInfo, isReportFull, pdfReportURL);

            vinInput.value = "";
            regNumberInput.value = "";
            bodyNumberInput.value = "";

            localStorage.setItem("carType", carType);
            localStorage.setItem("carQuery", carQuery);
            localStorage.setItem("requestUuid", requestUuid);

            if (isReportFull) {
                sendNotification("Отчет готов!")
            }
        } else {
            showError("Автомобиль не найден.");
        }
    } catch (error) {
        showError(`Ошибка запроса: ${error}`);
    } finally {
        loadingElement.classList.add("d-none");
    }
}

async function createPayment() {
    const loadingElement = document.getElementById("loading");
    loadingElement.classList.remove("d-none");

    try {
        const requestBody = JSON.stringify({ amount: 89.00, user_id: getUserId() });
        const response = await fetch(`${APIUrl}/payment/create`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: requestBody
        });

        if (!response.ok) {
            throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        window.location.href = data?.message?.confirmation?.confirmation_url || "#";
    } catch (error) {
        showError("Ошибка при создании платежа: " + error);
    } finally {
        loadingElement.classList.add("d-none");
    }
}

document.addEventListener("DOMContentLoaded", async function () {
    try {
        const processPayment = async () => {
            const paymentId = localStorage.getItem("paymentId")

            if (!paymentId) {
                return
            }

            const loadingElement = document.getElementById("loading");
            loadingElement.classList.remove("d-none");

            const requestBody = JSON.stringify({
                payment_id: paymentId,
                user_id: getUserId()
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

                    console.log("paymentPaid:", paymentPaid);
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

                        localStorage.removeItem("paymentId");
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
        }

        const processClearInputsOnSwitch = () => {
            const vinInput = document.getElementById("vin");
            const regNumberInput = document.getElementById("regNumber");
            const bodyNumberInput = document.getElementById("bodyNumber");

            const checkTabs = document.getElementById("checkTabs");

            checkTabs.addEventListener("click", function (event) {
                let targetTab = event.target.getAttribute("href");

                if (targetTab === "#vinCheck") {
                    regNumberInput.value = "";
                    vinInput.value = "";
                    bodyNumberInput.value = "";

                } else if (targetTab === "#regNumberCheck") {
                    regNumberInput.value = "";
                    vinInput.value = "";
                    bodyNumberInput.value = "";

                } else if (targetTab === "#bodyNumberCheck") {
                    regNumberInput.value = "";
                    vinInput.value = "";
                    bodyNumberInput.value = "";

                }
            });
        }

        const getAllReports = async () => {
            const userId = getUserId()
            const mainLoading = document.getElementById("main-loading");

            const requestBody = JSON.stringify({
                user_id: userId
            });

            try {
                const response = await fetch(`${APIUrl}/report/all`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: requestBody
                });

                if (!response.ok) {
                    let errorMessage = "Произошла ошибка";

                    try {
                        const data = await response.json();
                        if (data.detail) {
                            errorMessage = data.detail;
                        }
                    } catch (e) {
                        errorMessage = `Ошибка: ${response.status}`;
                    }
                    throw new Error(errorMessage);
                }

                const data = await response.json();
                const reports = data?.reports

                if (!reports) {
                    throw Error("Не удалось получить отчеты!")
                }

                const reportsModalElem = document.getElementById("reportsModalBody")

                if (!reports?.length) {
                    reportsModalElem.innerHTML += "<p>Здесь будут отображаться ваши заказы и отчеты.</p>";
                } else {
                    for (let report of reports) {

                        const reportData = report?.data?.content?.content
                        const reportPDF = `${APIUrl}/files/${report?.pdf_url}`

                        if (reportData) {

                            const brandLogoSrc = reportData?.tech_data?.brand?.logotype?.uri || "car-logo-placeholder.png";
                            const carTitleText = `${reportData?.tech_data?.brand?.name?.original || ""}
                                                  ${reportData?.tech_data?.model?.name?.original || ""},
                                                  ${reportData?.tech_data?.year || "Год неизвестен"}`;

                            const reportDateText = new Date().toLocaleDateString();
                            const plateNumberText = reportData?.identifiers?.vehicle?.reg_num || "Отсутствует";
                            const yearText = reportData?.tech_data?.year || "Нет данных";

                            const steeringText = reportData?.tech_data?.wheel?.position
                                ? (reportData.tech_data.wheel.position === "LEFT" ? "Левый руль" : "Правый руль")
                                : "Нет данных";

                            const powerText = reportData?.tech_data?.engine?.power?.hp
                                ? `${reportData.tech_data.engine.power.hp} л.с.`
                                : "Нет данных";

                            const vinText = reportData?.identifiers?.vehicle?.vin || "Нет VIN";
                            const bodyNumberText = reportData?.identifiers?.vehicle?.body || "Нет VIN";

                            const categoryText = reportData?.additional_info?.vehicle?.category?.code
                                ? `«${reportData.additional_info.vehicle.category.code}»`
                                : "Нет данных";

                            const engineText = reportData?.tech_data?.engine?.fuel?.type || "Нет данных";
                            const volumeText = reportData?.tech_data?.engine?.volume
                                ? `${reportData.tech_data.engine.volume} куб. см`
                                : "Нет данных";

                            reportsModalElem.innerHTML += `
                                <div class="container mt-5">
                                    <div class="card p-4 shadow">
                                        <div class="d-flex align-items-center mb-3">
                                            <img src="${brandLogoSrc}" alt="Логотип" style="height: 40px;">
                                            <h3 class="ms-3">${carTitleText}</h3>
                                        </div>
                                        <p class="text-muted">Отчет от <span>${reportDateText}</span></p>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <p><strong>Госномер:</strong> <span>${plateNumberText}</span></p>
                                                <p><strong>Год производства:</strong> <span>${yearText}</span></p>
                                                <p><strong>Руль:</strong> <span>${steeringText}</span></p>
                                                <p><strong>Мощность:</strong> <span>${powerText}</span> л.с.</p>
                                            </div>
                                            <div class="col-md-6">
                                                <p><strong>VIN:</strong> <span>${vinText}</span></p>
                                                <p><strong>Номер кузова:</strong> <span>${bodyNumberText}</span></p>
                                                <p><strong>Категория ТС:</strong> <span>${categoryText}</span></p>
                                                <p><strong>Двигатель:</strong> <span>${engineText}</span></p>
                                                <p><strong>Объем:</strong> <span>${volumeText}</span> куб. см</p>
                                            </div>
                                        </div>
                                        <div class="d-flex align-items-center justify-content-between mt-3 gap-2">
                                            <a target="_blank" href="${reportPDF}"
                                                class="btn btn-outline-dark w-100" download="">Скачать файл <i
                                                    class="bi bi-filetype-pdf"></i></a>
                                        </div>
                                    </div>
                                </div>`;

                        }

                    }
                }

                mainLoading.classList.add("d-none");
                processPayment()
                processClearInputsOnSwitch()
            } catch (error) {
                showError(`Ошибка запроса: ${error}`);
            }
        }


        const processUserId = async () => {
            try {

                const userId = getUserId()

                if (!userId) {
                    const response = await fetch(`${APIUrl}/user/create`);

                    if (!response.ok) {
                        throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();
                    const createdUserId = data?.user_id;

                    if (!createdUserId) {
                        throw new Error("Сервер вернул не корректный user_id")
                    }

                    localStorage.setItem("userId", createdUserId)
                }

                if (getUserId()) {
                    await getAllReports()
                }


            } catch (error) {
                showError(`Сайт не доступен для вас: ${error}`)
            }
        }

        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(reg => {
                    console.log("Service Worker зарегистрирован", reg);
                })
                .catch(err => {
                    console.error("Ошибка при регистрации Service Worker:", err);
                });
        }

        if (Notification.permission === "denied" || Notification.permission === "default") {
            Notification.requestPermission().then(permission => {
                if (permission === "denied") {
                    showError("Пожалуйста! Включите уведомления  для сайта. В ином случае вы не сможете получать уведомления!")
                }
            });
        }

        await processUserId()
    } catch (error) {
        showError(`Ошибка в DOMContentLoaded: ${error}`)
    }
});
