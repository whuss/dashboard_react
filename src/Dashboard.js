import React from "react";

import useDataApi from "./Fetch";

import { LoadingAnimation } from "./Toolbar";

const Dashboard = (props) => (
    <>
        <p>
            <b>Warning:</b> Obtaining the current status of the PTLs can take a long time.
        </p>
    </>
);

export default Dashboard;
