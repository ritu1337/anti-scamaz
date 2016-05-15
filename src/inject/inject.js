var patt = /imgur\.com\/(?:\S{1,15}\/)?(\w{5,8})\.*?(?:jpg|png|gif|gifv|jpeg|apng|bmp|webm|mp4|\/)?/i;
var get_imgur_id = window.location.href.match(patt);

if (get_imgur_id == null) {
    console.log('incorrect imgur');
} else {
    var imgur_id = get_imgur_id[1];
    console.log(imgur_id);
    imgur_url = window.location.href;
    
    if (imgur_url.indexOf("i.imgur.com") > -1) {
        console.log('loading');
        $("body").append(
            '<p id="loading" class="anti-scamaz" style="margin:20px 0 0 0;">Loading...</p>'
        );
    } else {
        $("#cta-container-placeholder").hide();
        $(".post-image:first").after(
            '<div id="loading" style="width: 640px;padding: 20px;background: #2B2B2B;border-radius: 5px;position: relative;">' +
            '<p style="padding:0;">Loading...</p></div>'
        );
    }

    $.ajax({
        'url': 'https://scamaz.xyz/check',
        'type': 'GET',
        'data': {
            'imgur_url': imgur_url
        },
        //The response from the server

        success: function(response) {
            var json_obj = response;

            $(document).ready(function() {
                $( "#loading" ).remove();
                if (imgur_url.indexOf("i.imgur.com") > -1) {
                    if (json_obj.status == 'ok') {
                        if (json_obj.is_scamaz) {
                            $("body").prepend(
                                '<h1 class="anti-scamaz" style="margin-bottom: 0px;background-color:black;color:red;">! SCAMAZ IMGUR BELOW !</h1><br><img id="wutface" style="height: 95vh" src="//scamaz.xyz/images/wutface.png"><br>'
                            );
                        }

                        $("body").append(
                            '<p class="anti-scamaz" style="margin:20px 0 0 0;">Format: <strong>' + json_obj.format + '</strong></p>' +
                            '<p class="anti-scamaz" style="margin:0;">Animated: <strong>' + (json_obj.is_animated ? 'Yes' : 'No') + '</strong></p>' +
                            (json_obj.is_animated ? '<p class="anti-scamaz" style="margin:0 0 0 0;">Duration: <strong>' + json_obj.duration + 's</strong></p>' : '') +
                            (json_obj.duration_warning ? '<p class="anti-scamaz" style="margin:0 0 0 0;"><span style="color:red;">Warning: </span><strong>' + json_obj.duration_warning + '</strong></p>' : '')
                        );

                        if (json_obj.is_scamaz) {
                            // Send a message to the event (background) page
                            chrome.runtime.sendMessage({
                                'action': 'update icon',
                            });
                        }
                    } else {
                        $("body").append(
                            '<p class="anti-scamaz" style="margin:20px 0 0 0;">Format: <strong>idk kev</strong></p>' +
                            '<p class="anti-scamaz" style="margin:20px 0 0 0;">Animated: <strong>idk kev</strong></p>'
                        );
                    }
                } else {
                    $( "#loading" ).remove();
                    if (json_obj.status == 'ok') {
                        if ((imgur_url.indexOf("imgur.com/gallery/") > -1) || (imgur_url.indexOf("imgur.com/a/") > -1)) {
                            $(".post-image:first").after(
                                '<div style="width: 640px;padding: 20px;background: #2B2B2B;border-radius: 5px;position: relative;">' +
                                '<p style="padding:0;">Gallery: <strong> Only the first image gets scanned</strong></p>' +
                                '<p style="padding:0;">Format: <strong>' + json_obj.format + '</strong></p>' +
                                '<p style="padding:0;">Animated: <strong>' + (json_obj.is_animated ? 'Yes' : 'No') + '</strong></p>' +
                                (json_obj.is_animated ? '<p style="padding:0;">Duration: <strong>' + json_obj.duration + 's</strong></p>' : '') +
                                (json_obj.duration_warning ? '<p style="padding:0;"><span style="color:red;">Warning: </span><strong>' + json_obj.duration_warning + '</strong></p>' : '') +
                                '</div>'
                            );
                        } else {
                            $(".post-image").after(
                                '<div style="width: 640px;padding: 20px;background: #2B2B2B;border-radius: 5px;position: relative;">' +
                                '<p style="padding:0;">Format: <strong>' + json_obj.format + '</strong></p>' +
                                '<p style="padding:0;">Animated: <strong>' + (json_obj.is_animated ? 'Yes' : 'No') + '</strong></p>' +
                                (json_obj.is_animated ? '<p style="padding:0;">Duration: <strong>' + json_obj.duration + 's</strong></p>' : '') +
                                (json_obj.duration_warning ? '<p style="padding:0;"><span style="color:red;">Warning: </span><strong>' + json_obj.duration_warning + '</strong></p>' : '') +
                                '</div>'
                            );
                        }
                    } else {
                        $(".post-image:first").after(
                            '<div style="width: 640px;padding: 20px;background: #2B2B2B;border-radius: 5px;position: relative;">' +
                            '<p style="padding:0;">Format: <strong>idk kev</strong></p>' +
                            '<p style="padding:0;">Animated: <strong>idk kev</strong></p></div>');
                    }
                }
            });
        },
        error: function(xhr, ajaxOptions, thrownError) {
            $(document).ready(function() {
                if (imgur_url.indexOf("i.imgur.com") > -1) {
                    $("body").append(
                        '<p class="anti-scamaz" style="margin:20px 0 0 0;">Format: <strong>idk kev</strong></p>' +
                        '<p class="anti-scamaz" style="margin:20px 0 0 0;">Animated: <strong>idk kev</strong></p>'
                    );
                } else {
                    $(".post-image:first").after(
                        '<div style="width: 640px;padding: 20px;background: #2B2B2B;border-radius: 5px;position: relative;">' +
                        '<p style="padding:0;">Format: <strong>idk kev</strong></p>' +
                        '<p style="padding:0;">Animated: <strong>idk kev</strong></p></div>');
                }
            });
        }
    });
}
