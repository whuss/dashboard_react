import React from "react";

import useDataApi from "./Fetch";

import { LoadingAnimation } from "./Toolbar";

import DeviceTable from "./DeviceTable";

function formatSingleSetting(setting) {
    const { cct, intensities } = setting;

    return (
        <>
            <td>{cct}</td>
            {intensities.map((i) => (
                <td>{i}</td>
            ))}
        </>
    );
}

function formatSetting(setting, area) {
    const { table, wall } = setting;

    if (area === "table") {
        return (
            <>
                <td>table</td>
                {formatSingleSetting(table)}
            </>
        );
    } else {
        return (
            <>
                <td>wall</td>
                {formatSingleSetting(wall)}
            </>
        );
    }
}

function formatFullSettings(timestamp, settings) {
    const { horizontal, vertical } = settings;

    return (
        <>
            <tr key={`horizontal_${timestamp}`}>
                <td rowSpan={4}>{timestamp}</td>
                <td rowSpan={2}>horizontal</td>
                {formatSetting(horizontal, "wall")}
            </tr>
            <tr>{formatSetting(horizontal, "table")}</tr>

            <tr key={`vertical_${timestamp}`}>
                <td rowSpan={2}>vertical</td>
                {formatSetting(vertical, "wall")}
            </tr>
            <tr>{formatSetting(vertical, "table")}</tr>
        </>
    );
}

function settingsTable(settings_list) {
    if (settings_list.length === 0) {
        return <></>;
    }

    return (
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th colSpan={2}>Area</th>
                    <th>CCT</th>
                    <th colSpan={12}>Intensities</th>
                </tr>
            </thead>
            <tbody>{settings_list.map(({ timestamp, settings }) => formatFullSettings(timestamp, settings))}</tbody>
        </table>
    );
}

function Settings(props) {
    const [{ data, isLoading, isError }] = useDataApi(`/backend/settings/${props.device}`, []);

    return (
        <LoadingAnimation isLoading={isLoading} isError={isError}>
            {settingsTable(data)}
        </LoadingAnimation>
    );
}

const TableHeader = () => (
    <>
        <th>Settings</th>
    </>
);

const TableRow = (props) => {
    return (
        <>
            <td>
                <Settings device={props.device_id} />
            </td>
        </>
    );
};

const AnalyticsSettings = (props) => (
    <DeviceTable format_header={TableHeader} format_row={TableRow} devices={props.devices} />
);

export default AnalyticsSettings;
