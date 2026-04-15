import express from "express";

import router from "./router.js";

const app = express();

app.use(express.json());

app.use("/api/v1", router);

app.listen(5000, () => {
  console.log("App is listening on port 5000......");
});
