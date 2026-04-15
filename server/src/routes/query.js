import express from "express";
import axios from "axios";
import env from "../config/env.js";

const app = express.Router();

app.post("/query", async (req, res, next) => {
  try {
    const { query, doc_id } = req.body;

    if (!query) {
      throw new Error("Invalid query!");
    }

    let aiRes;
    try {
      aiRes = await axios.post(
        `${env.AI_SERVICE_URL}/query`,
        {
          query: query,
          doc_id: doc_id,
        },
        {
          timeout: 30000,
        },
      );
    } catch (pyErr) {
      console.error("AI Service Error:", pyErr.message);
      return res.status(502).json({
        error: "AI service failed to process query",
        details: pyErr.response?.data || pyErr.message,
      });
    }

    res.status(200).json({
      answer: aiRes.data.answer,
      doc_id: aiRes.data.doc_id,
      sources: aiRes.data.sources,
    });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

export default app;
