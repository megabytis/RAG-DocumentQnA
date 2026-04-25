import express from "express";
import axios from "axios";
import env from "../config/env.js";

const app = express.Router();

app.post("/query", async (req, res, next) => {
  try {
    const { query, doc_ids } = req.body;

    if (!query || !doc_ids || doc_ids.length === 0) {
      return res.status(400).json({
        error: "Query and doc_ids array are required",
      });
    }

    let aiRes;
    try {
      aiRes = await axios.post(
        `${env.AI_SERVICE_URL}/query`,
        {
          query: query,
          doc_ids: doc_ids,
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
      doc_id: aiRes.data.doc_ids,
      sources: aiRes.data.sources,
      retrieved_chunks: aiRes.data.retrieved_chunks,
    });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

export default app;
