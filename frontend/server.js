// server.js
// Run:
//   npm i express cors dotenv @google/generative-ai
//   node server.js
//
// Test:
//   http://localhost:3000/api/latest
//   http://localhost:3000/api/models
//   POST http://localhost:3000/api/ai  (JSON body)

require("dotenv").config();
const express = require("express");
const cors = require("cors");
const { GoogleGenerativeAI } = require("@google/generative-ai");

const app = express();
app.use(cors());
app.use(express.json());

const API_KEY = process.env.GEMINI_API_KEY;
if (!API_KEY) {
  console.error("Missing GEMINI_API_KEY in .env");
}

const genAI = new GoogleGenerativeAI(API_KEY);

// ✅ Use a current model name (gemini-pro often 404s now)
const MODEL_NAME = "gemini-2.5-flash"; // if this 404s, try "gemini-2.0-flash"

// Demo sensor values (later replace with database)
app.get("/api/latest", (req, res) => {
  res.json({
    temperature: -1.8,
    humidity: 82,
    wetnessRaw: 2800,
    updated: new Date().toISOString(),
  });
});

// Helpful debug: list available models for YOUR key
app.get("/api/models", async (req, res) => {
  try {
    const models = await genAI.listModels();
    // return just names to keep it clean
    res.json(models.models?.map(m => m.name) ?? models);
  } catch (e) {
    console.error("listModels error:", e);
    res.status(500).json({ error: "listModels failed", details: String(e) });
  }
});

app.post("/api/ai", async (req, res) => {
  const { temperature, humidity, wetnessRaw } = req.body;

  const prompt = `
You are an AI system detecting black ice risk on roads.

Sensor Inputs:
- Temperature: ${temperature} °C
- Humidity: ${humidity} %
- Wetness sensor: ${wetnessRaw} (0-4095)

Classify risk as LOW, MEDIUM, or HIGH.
Return ONLY JSON in this exact format:
{"risk":"LOW|MEDIUM|HIGH","message":"one short sentence","actions":["action1","action2"]}
`;

  try {
    const model = genAI.getGenerativeModel({ model: MODEL_NAME });
    const result = await model.generateContent(prompt);
    const text = result.response.text();

    // Extract JSON safely
    const start = text.indexOf("{");
    const end = text.lastIndexOf("}");
    if (start === -1 || end === -1) {
      return res.json({
        risk: "MEDIUM",
        message: "AI response was not JSON. Try again.",
        actions: ["monitor sensors"],
        raw: text,
      });
    }

    const json = JSON.parse(text.slice(start, end + 1));
    res.json(json);
  } catch (err) {
    console.error("Gemini error:", err);
    res.status(500).json({
      risk: "UNKNOWN",
      message: "Gemini request failed. Check model name or API key.",
      actions: [],
      error: String(err),
      model: MODEL_NAME,
    });
  }
});

app.listen(3000, () => {
  console.log("Backend running on http://localhost:3000");
  console.log("Try: http://localhost:3000/api/models");
});
