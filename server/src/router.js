import fileUploadRouter from "./routes/file-upload.js";
import queryRouter from "./routes/query.js";
import express from "express";

const router = express();

router.use(fileUploadRouter);
router.use(queryRouter);

export default router;
