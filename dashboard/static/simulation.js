(function () {
    const template = document.getElementById("attackTemplate");
    if (!template) return;

    const fields = {
        behFlood: document.getElementById("behFlood"),
        behUnauthorized: document.getElementById("behUnauthorized"),
        behUnknown: document.getElementById("behUnknown"),
        behAbnormal: document.getElementById("behAbnormal"),
        behMalformed: document.getElementById("behMalformed"),
        deviceId: document.getElementById("deviceId"),
        topic: document.getElementById("topic"),
        sensorType: document.getElementById("sensorType"),
        sensorValue: document.getElementById("sensorValue"),
        payloadType: document.getElementById("payloadType"),
        attackMode: document.getElementById("attackMode"),
        repeatCount: document.getElementById("repeatCount"),
        delayMs: document.getElementById("delayMs"),
        repeatGroup: document.getElementById("repeatGroup")
    };

    const preview = {
        attackType: document.getElementById("previewAttackType"),
        device: document.getElementById("previewDevice"),
        topic: document.getElementById("previewTopic"),
        messages: document.getElementById("previewMessages"),
        detection: document.getElementById("expectedDetection")
    };

    const status = {
        attackStatus: document.getElementById("attackStatus"),
        messagesSent: document.getElementById("messagesSent"),
        duration: document.getElementById("attackDuration")
    };

    const executeButton = document.getElementById("executeAttackBtn");
    const stopButton = document.getElementById("stopAttackBtn");

    let attackTimer = null;
    let attackStartTime = null;
    let estimatedMessagesSent = 0;

    const templateDefaults = {
        flood: {
            name: "Flood Attack",
            flood: true,
            unauthorized: false,
            unknown: false,
            abnormal: false,
            malformed: false,
            device: "attacker_flood_01",
            topic: "home/temperature",
            value: "30",
            payloadType: "json",
            repeat: "150",
            delay: "10"
        },
        unauthorized: {
            name: "Unauthorized Topic Attack",
            flood: false,
            unauthorized: true,
            unknown: false,
            abnormal: false,
            malformed: false,
            device: "attacker_unauthorized_01",
            topic: "admin/control",
            value: "30",
            payloadType: "json",
            repeat: "1",
            delay: "100"
        },
        abnormal: {
            name: "Abnormal Value Attack",
            flood: false,
            unauthorized: false,
            unknown: false,
            abnormal: true,
            malformed: false,
            device: "temp_sensor_01",
            topic: "home/temperature",
            value: "999",
            payloadType: "json",
            repeat: "1",
            delay: "100"
        },
        malformed: {
            name: "Malformed Payload Attack",
            flood: false,
            unauthorized: false,
            unknown: false,
            abnormal: false,
            malformed: true,
            device: "temp_sensor_01",
            topic: "home/temperature",
            value: "999",
            payloadType: "malformed",
            repeat: "1",
            delay: "100"
        },
        hybrid: {
            name: "Hybrid Attack",
            flood: true,
            unauthorized: true,
            unknown: true,
            abnormal: true,
            malformed: false,
            device: "attacker_custom_01",
            topic: "admin/control",
            value: "999",
            payloadType: "json",
            repeat: "150",
            delay: "10"
        },
        custom: {
            name: "Custom Attack",
            flood: false,
            unauthorized: false,
            unknown: false,
            abnormal: false,
            malformed: false,
            device: "custom_device_01",
            topic: "home/temperature",
            value: "30",
            payloadType: "json",
            repeat: "10",
            delay: "100"
        }
    };

    function applyTemplate() {
        const data = templateDefaults[template.value];
        if (!data) return;

        fields.behFlood.checked = data.flood;
        fields.behUnauthorized.checked = data.unauthorized;
        fields.behUnknown.checked = data.unknown;
        fields.behAbnormal.checked = data.abnormal;
        fields.behMalformed.checked = data.malformed;
        fields.deviceId.value = data.device;
        fields.topic.value = data.topic;
        fields.sensorValue.value = data.value;
        fields.payloadType.value = data.payloadType;
        fields.repeatCount.value = data.repeat;
        fields.delayMs.value = data.delay;

        updatePreview();
    }

    function getBehaviours() {
        const behaviours = [];

        if (fields.behFlood.checked) behaviours.push("flood");
        if (fields.behUnauthorized.checked) behaviours.push("unauthorized");
        if (fields.behUnknown.checked) behaviours.push("unknown");
        if (fields.behAbnormal.checked) behaviours.push("abnormal");
        if (fields.behMalformed.checked) behaviours.push("malformed");

        return behaviours;
    }

    function buildAttackConfig() {
        return {
            template: template.value,
            behaviours: getBehaviours(),
            device_id: fields.deviceId.value,
            topic: fields.topic.value,
            sensor_type: fields.sensorType.value,
            sensor_value: fields.sensorValue.value,
            payload_type: fields.payloadType.value,
            mode: fields.attackMode.value,
            repeat_count: fields.repeatCount.value,
            delay_ms: fields.delayMs.value
        };
    }

    function updatePreview() {
        const selectedTemplate = template.options[template.selectedIndex].text;
        preview.attackType.textContent = selectedTemplate;
        preview.device.textContent = fields.deviceId.value || "-";
        preview.topic.textContent = fields.topic.value || "-";

        if (fields.attackMode.value === "infinite") {
            preview.messages.textContent = "Infinite until stopped";
            fields.repeatGroup.classList.add("hidden-field");
        } else {
            preview.messages.textContent = fields.repeatCount.value || "0";
            fields.repeatGroup.classList.remove("hidden-field");
        }

        const detections = [];

        if (fields.behFlood.checked) detections.push("MQTT Flooding");
        if (fields.behUnauthorized.checked) detections.push("Unauthorized Topic Access");
        if (fields.behUnknown.checked) detections.push("Unknown Device");
        if (fields.behAbnormal.checked) detections.push("Abnormal Sensor Value");
        if (fields.behMalformed.checked || fields.payloadType.value === "malformed") detections.push("Malformed Payload");

        preview.detection.innerHTML = "";

        if (detections.length === 0) {
            const li = document.createElement("li");
            li.textContent = "Normal / No expected alert";
            preview.detection.appendChild(li);
        } else {
            detections.forEach(item => {
                const li = document.createElement("li");
                li.textContent = "✓ " + item;
                preview.detection.appendChild(li);
            });
        }
    }

    function startLocalStatus(mode, repeatCount, delayMs) {
        attackStartTime = Date.now();
        estimatedMessagesSent = 0;

        status.attackStatus.textContent = "🔴 Running";
        status.attackStatus.className = "status-running";
        executeButton.disabled = true;
        stopButton.disabled = false;

        attackTimer = setInterval(function () {
            const elapsedSeconds = Math.floor((Date.now() - attackStartTime) / 1000);
            const minutes = String(Math.floor(elapsedSeconds / 60)).padStart(2, "0");
            const seconds = String(elapsedSeconds % 60).padStart(2, "0");

            status.duration.textContent = minutes + ":" + seconds;

            if (mode === "infinite") {
                estimatedMessagesSent = Math.floor((elapsedSeconds * 1000) / delayMs);
            } else {
                estimatedMessagesSent = Math.min(
                    repeatCount,
                    Math.floor((elapsedSeconds * 1000) / delayMs)
                );

                if (estimatedMessagesSent >= repeatCount) {
                    stopLocalStatus("🟢 Completed");
                }
            }

            status.messagesSent.textContent = estimatedMessagesSent;
        }, 500);
    }

    function stopLocalStatus(label) {
        if (attackTimer) {
            clearInterval(attackTimer);
            attackTimer = null;
        }

        status.attackStatus.textContent = label || "🟢 Idle";
        status.attackStatus.className = "status-idle";
        executeButton.disabled = false;
        stopButton.disabled = true;
    }

    async function executeCustomAttack() {
        const config = buildAttackConfig();

        const repeatCount = parseInt(config.repeat_count || "1", 10);
        const delayMs = parseInt(config.delay_ms || "100", 10);

        try {
            const response = await fetch("/simulate/custom", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                alert(result.message || "Failed to start custom attack.");
                return;
            }

            startLocalStatus(config.mode, repeatCount, delayMs);

        } catch (error) {
            alert("Error starting custom attack: " + error);
        }
    }

    async function stopCustomAttack() {
        try {
            const response = await fetch("/simulate/custom/stop", {
                method: "POST"
            });

            const result = await response.json();

            if (result.success) {
                stopLocalStatus("🟢 Stopped");
            } else {
                alert(result.message || "No running attack to stop.");
            }

        } catch (error) {
            alert("Error stopping custom attack: " + error);
        }
    }

    Object.values(fields).forEach(element => {
        if (element) {
            element.addEventListener("input", updatePreview);
            element.addEventListener("change", updatePreview);
        }
    });

    template.addEventListener("change", applyTemplate);

    if (executeButton) {
        executeButton.addEventListener("click", executeCustomAttack);
    }

    if (stopButton) {
        stopButton.addEventListener("click", stopCustomAttack);
    }

    updatePreview();
})();