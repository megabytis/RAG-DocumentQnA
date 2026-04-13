import express from "express";

const app = express();

import fileUploadRouter from "./routes/file-upload.js";

app.get("/me", (req, res, next) => {
  res.send("Hey there Miku!");
});

app.use("/api/v1/", fileUploadRouter);

app.listen(5000, () => {
  console.log("App is listening on port 5000......");
});
