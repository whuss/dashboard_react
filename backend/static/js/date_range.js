$(function() {
    // Set initial time range for database query
    var range_start = moment().startOf('day');
    var range_end = moment();

    // If current url contains a valid date range use this as the default
    const urlParams = new URLSearchParams(window.location.search);
    const url_range_start = moment(urlParams.get('start'));
    const url_range_end = moment(urlParams.get('end'));

    if (url_range_start.isValid())
    {
        range_start = url_range_start;
    }

    if (url_range_end.isValid())
    {
        range_end = url_range_end;
    }

    // Callback for time range picker
    function cb(start, end) {
        $('#reportrange span').html(start.format('MMMM D, YYYY HH:mm') + ' - ' + end.format('MMMM D, YYYY HH:mm'));
        range_start = start;
        range_end = end;
    }

    $('#reportrange').daterangepicker({
        timePicker: true,
        timePicker24Hour: true,
        startDate: range_start,
        endDate: range_end,
        ranges: {
           // Predefined time ranges
           'Today': [moment().startOf('day'), moment()],
           'Yesterday': [moment().subtract(1, 'days').startOf('day'), moment().subtract(1, 'days').endOf('day')],
           'Last 2 days': [moment().subtract(2, 'days').startOf('day'), moment()],
           'Last week': [moment().subtract(6, 'days').startOf('day'), moment()]
        }
    }, cb);

    cb(range_start, range_end);

    $('#run_query').click(function() {
        var start = range_start.format("YYYY-MM-DD HH:mm:ss");
        var end = range_end.format("YYYY-MM-DD HH:mm:ss");
        var loc = window.location;
        var currentURL = loc.protocol + '//' + loc.host + loc.pathname;
        window.location = currentURL +"?start=" + start + "&end=" + end;
    });
});