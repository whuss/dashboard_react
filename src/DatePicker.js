import "./App.css";

import React, { useState } from "react";

import moment from "moment";

import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";
import InputGroup from "react-bootstrap/InputGroup";
import FormControl from "react-bootstrap/FormControl";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Popover from "react-bootstrap/Popover";
import Overlay from "react-bootstrap/Overlay";

import { Helmet } from "react-helmet";
import DayPicker, { DateUtils } from "react-day-picker";
import DayPickerInput from "react-day-picker/DayPickerInput";
import "react-day-picker/lib/style.css";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCalendar } from "@fortawesome/free-solid-svg-icons";

function formatDate(date) {
    return moment(date).format("YYYY-MM-DD");
}

function parseDate(dateStr) {
    return moment(dateStr, "YYYY-MM-DD");
}

const DayPickerFormat = () => (
    <Helmet>
        <style>
            {`
.DayPicker {
font-size: 0.8rem;
}
.DayPicker-Body {
line-height: 1;
}
.Selectable .DayPicker-Day--selected:not(.DayPicker-Day--start):not(.DayPicker-Day--end):not(.DayPicker-Day--outside) {
background-color: #f0f8ff !important;
color: #4a90e2;
}
.Selectable .DayPicker-Day {
border-radius: 0 !important;
}
.Selectable .DayPicker-Day--start {
border-top-left-radius: 10% !important;
border-bottom-left-radius: 10% !important;
}
.Selectable .DayPicker-Day--end {
border-top-right-radius: 10% !important;
border-bottom-right-radius: 10% !important;
}
`}
        </style>
    </Helmet>
);

function useDateRangeWidget(_from, _to) {
    const [range, setRange] = useState({ from: _from, to: _to });
    const { from, to } = range;
    const modifiers = { start: from, end: to };

    function changeRange(day) {
        if (day === from) {
            setRange({ from: day, to: day });
        } else {
            setRange(DateUtils.addDayToRange(day, range));
        }
    }

    const dayPicker = (
        <>
            <DayPicker
                className="Selectable"
                month={from}
                numberOfMonths={2}
                selectedDays={[from, { from, to }]}
                modifiers={modifiers}
                onDayClick={changeRange}
            />
            <DayPickerFormat />
        </>
    );
    return [from, to, dayPicker];
}

function useDateRange(_from, _to) {
    const [from, to, dateRangePicker] = useDateRangeWidget(_from, _to);

    function formatDateRange() {
        let f = from && formatDate(from);
        let t = to && formatDate(to);
        return `${f} - ${t}`;
    }

    const overlay = (props) => (
        <Popover id="datepicker-popup" {...props}>
            <Popover.Content>{dateRangePicker}</Popover.Content>
        </Popover>
    );

    const inputElement = (
        <ButtonGroup>
            <span className="label">Time&nbsp;range:</span>
            <InputGroup>
                <FormControl value={formatDateRange()} />
                <InputGroup.Append>
                    <InputGroup.Text><FontAwesomeIcon icon={faCalendar} /></InputGroup.Text>
                </InputGroup.Append>
            </InputGroup>
            </ButtonGroup>
    );

    const dateRangeWidget = (
        <>
            <OverlayTrigger rootClose placement="bottom" trigger="click" overlay={overlay}>
                {inputElement}
            </OverlayTrigger>
        </>
    );

    return [from, to, dateRangeWidget];
};

export default useDateRange;
export { formatDate, parseDate };
