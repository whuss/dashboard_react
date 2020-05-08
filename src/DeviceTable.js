import React from "react";

import Toolbar, { useDeviceFilter } from "./Toolbar";

function DeviceTable(props) {
    const [selectedDevices, setFilterStr] = useDeviceFilter();

    return (
        <>
            <Toolbar>{setFilterStr}</Toolbar>
            {props.format_table(selectedDevices)}
        </>
    );
}

export default DeviceTable;
