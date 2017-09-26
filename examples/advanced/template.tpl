<!DOCTYPE html>
<head>
    <style>
    .low {
        color: #D8000C;
        background-color: #FFBABA;
    }

    .mid {
        color: #9F6000;
        background-color: #FEEFB3;
    }

    .high {
        color: #4F8A10;
        background-color: #DFF2BF;
    }
    </style>
</head>

<body>
    <h1>My Rendered {{ payload.project }}</h1>

    <h2>Timestamp:</h2>

    <ul>
        <li>Epoch: {{ data.timestamp.epoch }}</li>
        <li>ISO8601: {{ data.timestamp.iso8601 }}</li>
    </ul>

    <h2>User:</h2>

    <ul>
        <li>UID: {{ data.user.uid }}</li>
        <li>Login: {{ data.user.login }}</li>
    </ul>

    <h2>Coverage:</h2>

    {% for filename, filedata in data.coverage.files.items() %}
    <ul>
       <li class="{{ filedata.line_rate|coverage_class }}">
           {{ filename }} : {{ filedata.line_rate }}
       </li>
    </ul>
    {% endfor %}
</body>