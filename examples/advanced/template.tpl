{% import "colors.tpl" as colors %}

<!DOCTYPE html>
<head>
    <style>
    .low {
        color: {{ colors.low }};
        background-color: {{ colors.low_background }};
    }

    .mid {
        color: {{ colors.mid }};
        background-color: {{ colors.mid_background }};
    }

    .high {
        color: {{ colors.high }};
        background-color: {{ colors.high_background }};
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