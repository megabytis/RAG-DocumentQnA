import express from "express";

const app = express();

app.get("/me", (req, res, next) => {
  res.send("Hey there Miku!");
});

app.listen(5000, () => {
  console.log("App is listening on port 5000......");
});
