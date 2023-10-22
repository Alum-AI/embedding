import * as React from "react";
import { createHashRouter } from "react-router-dom";

import App from "./App";
import Home from "./pages/Home";
import Student from "./pages/Student/Student";
import Example from "./pages/Example";

export const appRouter = createHashRouter([
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "/student",
    element: <Student />,
  },
  {
    path: "/example",
    element: <Example />,
  },
]);
