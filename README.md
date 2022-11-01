# Flask Hyper TOC

An implementation of a dynamic table of contents using [Hyperscript](https://hyperscript.org/). Code here made for Flask, but with small modifications it should work with Django or any other library.

https://user-images.githubusercontent.com/3788301/199255762-b3983483-b323-49e2-84aa-d2773e0f8f17.mp4


## Getting started

Install dependencies:

```bash
pip install -r requirements.txt
```

### TailwindCSS

The repo comes with a minified CSS in `static/css/output.css`, but if you want to compile your own, you'll need to install TailwindCSS first:

```bash
npm install
```

And then watch the files for changes:

```bash
npx tailwindcss -i ./app/css/style.css -o ./app/static/css/output.css --watch
```

That will watch the files for changes while you work with them. If you want to build the output CSS minified, use:

```bash
npx tailwindcss -i ./app/css/style.css -o ./app/static/css/output.css --minify
```

## How to use the components

There are three pre-built components that are used in conjunction to build the page content and the table of contents:

- `with_side_index`, inside [`app/templates/layouts/side-index.html`](app/templates/layouts/side-index.html).
- `section`, inside [`app/templates/components/section/section.html`](app/templates/components/section/section.html).
- `section_header`, inside [`app/templates/components/section/section-header.html`](app/templates/components/section/section-header.html) (you seldom will use this one manually).

The `with_side_index` and `section` components are ["Higher-Order Components"](https://jinja.palletsprojects.com/en/3.0.x/templates/#call). This means that you must use them with a `call` block, like so:

```jinja
{% call with_side_index(".section-header") %}
    {% call section("Description") %}
        <p class="text-2xl font-semibold">This is in the first section.</p>
    {% endcall %}

    {% call section("Something else") %}
        <p>This is in the second section.</p>
    {% endcall %}

    {% call section("A third one") %}
        <p>You can put as many HTML elements as you want.</p>
        <p>Inside each caller block.</p>
    {% endcall %}
{% endcall %}
```

Optionally you can pass classes to each section:

```jinja
{% call section("Section title", class_="mb-24 prose") %}

{% endcall %}
```

## How the dynamic highlighting works

If you look at [`layouts/side-index.html`](app/templates/layouts/side-index.html), you'll see that the `with_side_index` macro takes in one optional argument: `target`:

```jinja
{% macro with_side_index(target="h1") %}
```

This signals what elements will be used to populate the table of contents. Any Hyperscript selector will work here, so you can pass `.section` for example, and that will generate an entry in the table of contents for each element with the `section` class in the whole document.

Still inside the same file, skip the `template` tag for now, we'll come back to it. Let's go to this `div`:

```html
<div 
    _="init
        repeat for title in <{{target}}/>
            make a <div.index-element /> called item
            put the innerHTML of <#side-index-link /> into item
            set link to the first <a/> in item
            set link.href to '#' + the title's id
            set headerTitle to the first .header-title in title
            set indexTitle to the first .index-title in link
            put the headerTitle's textContent into indexTitle's textContent
            put item before me
        end
    end
    ">
    </div>
```

This rather long Hyperscript code is fairly readable (I think!). It iterates over all the elements that are returned by the `target` parameter, and then copies the `template` tag above. Each `template` tag has an `a` element inside it, which gets its `textContent` replaced so it matches the target, and its `href` replaced to it links to the target.

### Links in each target

Each target should have an anchor link, such as `#section-one`. The [`components/section/section.html`](app/templates/components/section/section.html) has an `id` property which can be given as an argument, or it is generated from the heading title using the `python-slugify` library.

## Highligting the ToC items in view

As you scroll, you'll notice that the ToC items get more or less opaque depending on whether the section that is currently in view matches the link in the ToC.

This is done using the Intersection Observer API.

Whenever 20% of a `section` component enters view, a Hyperscript event is fired (`showYourself`). When less than 20% of a section remains in view, another Hyperscript event is fired (`hideYourself`).

This is what that code looks like:

```jinja
<section class="{{ class_ }}" id="{{ section_id }}"
    _="on intersection(intersecting) having threshold 0.2
            if intersecting
                wait 100ms
                send showYourself(id:'#{{ section_id }}') to <a /> in #side-index-layout
            else
                wait 100ms
                send hideYourself(id:'#{{ section_id }}') to <a /> in #side-index-layout
            end
        end"
>
    ...
</section>
```

This event passes an argument, `id`, which is a string equal to the ID selector of the section that has just entered or left view, such as `#section-one`.

Then let's go back to `layouts/side-index.html` and look at the `template` tag.

This looks at the `showYourself` and `hideYourself` events, and adds or removes an opacity class depending on whether the `id` argument passed in the event matches the `href` property of the link:

```html
<template id="side-index-link">
    <a
        href="#"
        class="p-0 cursor-pointer flex items-center mb-4 no-underline opacity-50 hover:opacity-100 transition-opacity"
        _="on showYourself(id) queue all
            if @href == id then
                remove .opacity-50 from me
            end
        end
        on hideYourself(id) queue all
            if @href == id then
                add .opacity-50 to me
            end
        end
        "
    >
        <span class="index-title link-item"></span>
    </a>
</template>
```

Overall this is a bit convoluted, but an equivalent React set of components, which I also implemented for a different project, isn't any simpler. Especially when you take into account navigating to a URL with an anchor, such as `http://127.0.0.1:5000/#section-one`.

With React and NextJS, handling this was a supreme pain in the butt. A very convenient workaround here is adding the `wait 100ms` before firing the `showYourself` or `hideYourself` events.
