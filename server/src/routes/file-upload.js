import express from "express";
import multer, { MulterError } from "multer";
import path from "path";
import { randomUUID } from "crypto";
import fs from "fs";
import axios from "axios";
import env from "../config/env.js";

const app = express.Router();

// configurign storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "data/raw_docs/");
  },
  filename: (req, file, cb) => {
    const uniqueName = randomUUID() + path.extname(file.originalname);
    cb(null, uniqueName);
  },
});

// filtering file
const fileFilter = (req, file, cb) => {
  const allowdFileTypes = [
    "application/pdf",
    "text/plain",
    "application/msword",
  ];

  if (allowdFileTypes.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new Error("Invalid file type. Only PDF, TXT, DOC allowed."), false);
  }
};

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: { fileSize: 10 * 1024 * 1024 },
});

// checkign uploads directory , creating one if not present
if (!fs.existsSync("data/raw_docs/")) {
  fs.mkdirSync("data/raw_docs/", { recursive: true });
}

// upload endpoint
app.post("/file/upload", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        error: "No file uploaded",
      });
    }

    const docId = randomUUID();

    // file info
    const fileData = {
      originalname: req.file.originalname,
      filename: docId + path.extname(req.file.originalname),
      path: req.file.path,
      size: req.file.size,
      mimetype: req.file.mimetype,
    };

    let aiRes;
    try {
      aiRes = await axios.post(`${env.AI_SERVICE_URL}/ingest`, {
        doc_id: docId,
        file_path: path.resolve(req.file.path),
      });
    } catch (pyErr) {
      fs.unlinkSync(req.file.path);
      return res.status(502).json({
        error: "AI service failed to process file",
      });
    }

    res.status(200).json({
      message: "File upload successfully",
      doc_id: docId,
      chunks: aiRes.data.chunks,
      file: fileData,
    });
  } catch (err) {
    res.status(500).json({
      error: err.message,
    });
  }
});

export default app;
