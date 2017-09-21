<!DOCTYPE html>

<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Test Summary</title>
</head>

<body>
    <header>
        <h1>Test Summary</h1>
        <table>
                <tr>
                    <th>Timestamp:</th>
                    <td>{{ data.timestamp.iso8601 }}</td>
                </tr>
                <tr>
                    <th>Status:</th>
                    <td>FIXME</td>
                </tr>
                <tr>
                    <th>Build:</th>
                    <td><a href="{{ data.jenkins.build_url }}">{{ data.jenkins.build_number }}</a></td>
                </tr>
                <tr>
                    <th>Git:</th>
                    <td>{{ data.git.rev }} by {{ data.git.name }} &lt;{{ data.git.email }}&gt;</td>
                </tr>
        </table>
    </header>

    <section>

    </section>

    <footer>
        <a href="{{ payload.project_url }}">{{ payload.project_name }}</a>
    </footer>
</body>

</html>
