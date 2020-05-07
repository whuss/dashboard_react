import React from "react";

import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

import { PlotDevice } from "./BokehPlot";

import useDataApi from "./Fetch";

function AnalyticsScenes() {
    const [{ data, isLoading, isError }, doFetch] = useDataApi("/backend/devices", []);

    return (
        <>
            {isError && <div>Something went wrong ...</div>}

            {isLoading ? (
                <div>Loading ...</div>
            ) : (
                <Table className={"dataTable"} hover>
                    <thead>
                        <tr>
                            <th>Device ID</th>
                            <th>Cycles</th>
                            <th>Download</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((device) => (
                            <tr key={device}>
                                <th>{device}</th>
                                <td>
                                    <PlotDevice src={"/backend/plot_analytics_scenes"} device={device} />
                                </td>
                                <td>
                                    <Button>Download</Button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            )}
        </>
    );
}

export default AnalyticsScenes;
