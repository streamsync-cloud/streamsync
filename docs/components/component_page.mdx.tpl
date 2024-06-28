---
title: {{ name }}
mode: "wide"
---

{{ description }}

<img src="/framework/public/components/{{type}}.png" />

{{ docs }}

{% if fields %}
## Fields

<table className="componentFields">
	<thead>
		<th>Name</th>
		<th>Type</th>
		<th class="desc">Description</th>
		<th>Options</th>
	</thead>
	<tbody>
		{% for _, field in fields %}
		<tr>
			<td>{{ field.name }}</td>
			<td>{{ field.type }}</td>
			<td>{{ field.desc }}</td>
			<td>
				<ol>
					{% for _, option in field.options %}
					<li>{{ option }}</li>
					{% endfor %}
				</ol>
			</td>
		</tr>
		{% endfor %}
	</tbody>
</table>
{% endif %}

{% if events %}
## Events
<AccordionGroup>
  {% for event, eventInfo in events %}
  <Accordion title="{{ event }}" icon="code">
    {{ eventInfo.desc }}

    ```python
	{{ eventInfo.stub | safe }}
	```
  </Accordion>
  {% endfor %}
</AccordionGroup>
{% endif %}

## Low code usage

This component can be declared directly in Python, using [backend-driven UI](../backend-driven-ui).

```python
{{ low_code_usage | safe }}
```

{% if events %}
A function, in this example `handle_event`, should be implemented in your code to handle events.
```python
{{ event_handler | safe }}
```
{% endif %}


## Reference

* <a href="https://github.com/writer/writer-framework/blob/dev/src/ui/{{fileRef}}" target="_blank" >Explore this component's source code on GitHub</a>
