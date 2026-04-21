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
    const docId = randomUUID();
    file.docId = docId;
    const uniqueName = docId + path.extname(file.originalname);
    cb(null, uniqueName);
  },
});

// filtering file
const fileFilter = (req, file, cb) => {
  const allowedFileTypes = [
    "application/pdf",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // .docx
  ];

  if (allowedFileTypes.includes(file.mimetype)) {
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
app.post("/file/upload", upload.array("files", 5), async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({
        error: "No file uploaded",
      });
    }

    const results = [];
    const failuers = [];

    // now passing each file individually
    for (const file of req.files) {
      const docId = file.docId;

      const fileData = {
        filename: file.originalname,
        path: file.path,
        size: file.size,
        mimetype: file.mimetype,
      };

      let aiRes;
      try {
        aiRes = await axios.post(
          `${env.AI_SERVICE_URL}/ingest`,
          {
            doc_id: docId,
            file_path: path.resolve(file.path),
          },
          {
            timeout: 30000,
          },
        );

        results.push({
          status: "success",
          doc_id: docId,
          chunks: aiRes.data.chunks || 0,
          file: fileData,
        });
      } catch (pyErr) {
        if (fs.existsSync(file.path)) {
          fs.unlinkSync(file.path);
        }
        // above fs.unlinkSync() is a Node.js method that deletes a file from the filesystem.
        // When AI Service Fails, we have to remove the existing uploaded file from disk
        failuers.push({
          file: file.originalname,
          error: pyErr.response?.data || pyErr.message,
        });
      }
    }

    if (results.length === 0) {
      return res.status(502).json({
        error: "AI service failed to process all files",
        failuers,
      });
    }

    res.status(200).json({
      message: `Successfully processed ${results.length} of ${req.files.length} file(s)`,
      uploaded: results,
      failed: failuers.length > 0 ? failuers : undefined,
    });
  } catch (err) {
    // Now cleaning up ALL uploaded files on unexpected error
    if (req.files && Array.isArray(req.files)) {
      req.files.forEach((file) => {
        if (fs.existsSync(file.path)) {
          fs.unlinkSync(file.path);
        }
      });
    }

    console.error("Upload Error:", err);
    res.status(500).json({
      error: err.message,
    });
  }
});

export default app;
