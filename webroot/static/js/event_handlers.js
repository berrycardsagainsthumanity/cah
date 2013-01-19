cah.eventHandlers = (function () {
    var notify_sound = new Audio("static/sounds/yay.wav");
    var window_focused = true;
    var notify_interval = null;
    var window_title = "Cards against humanity";
    var notify_title = "Your turn!";

    var max_card_height = 160;
    var max_card_width = 125;
    var max_card_font_size = 80;

    var card_size_css_rule;
    var ss = document.styleSheets;
    for (var i = 0; i < document.styleSheets.length; ++i) {
        if (ss[i].href && ss[i].href.indexOf('js/cah.css') !== 0) {
            for (var j = 0; j < ss[i].cssRules.length; ++j) {
                if (ss[i].cssRules[j].selectorText == ".card") {
                    card_size_css_rule = ss[i].cssRules[j] ?
                        ss[i].cssRules[j] : ss[i].rules[j];
                    console.log("Found card css rule: ", card_size_css_rule);
                }
            }
        }
    }

    var clear_notify_interval = function () {
        if (notify_interval) {
            try {
                clearInterval(notify_interval);
            }
            catch (ex) {
            }
        }
        // If this isn't in a timeout it doesn't work for some reason.
        // Probably to do with canceling the interval.
        setTimeout(function () {
            document.title = window_title;
        }, 50);

    };

    $(window).focus(function () {
        window_focused = true;
        clear_notify_interval();
    }).blur(function () {
            window_focused = false;
        });
    $("body").click(function () {
        clear_notify_interval();
    });

    var notify = function () {
        if ($('.afk_checkbox').prop("checked")) {
            return;
        }
        if ($('.notify').is(':checked')) {
            notify_sound.play();
        }
        if (!window_focused) {
            notify_interval = setInterval(function () {
                if (document.title == window_title)
                    document.title = notify_title;
                else
                    document.title = window_title;
            }, 1000);
        }
    };

    return {
        sync_users:function (topic, users) {
            var $users = $('.users').html(ich.t_users(users));
            if (cah.admin_pass) {
                $('.kick_user').css("display", "inline");
            }

            cah.CHATLIST = [];
            for (var i in users.users) {
                user = users.users[i];
                cah.CHATLIST.push(user.username);
                if (user.username == cah.username) {
                    $('.afk_checkbox').prop("checked", user.afk);
                }
            }
        },
        send_hand:function (topic, cards) {
            $('.hand').html(ich.t_white_cards(cards));
        },
        add_black:function (topic, card) {
            $(ich.t_black_card(card)).appendTo('.play_area_black');
        },
        white_chosen:function () {
            $(ich.t_white_card()).appendTo('.play_area_whites');
        },
        czar_chosen:function (topic, username) {
            if (username == cah.username) {
                $('.play_area_overlay').show();
                $('.play_area_overlay_text').text('Waiting for players');
                $('.hand_overlay_text').text('You are the card Czar');
                $(".hand_overlay").show();
                cah.czar = true;
                cah.restarted_timer = false;
            }
            else {
                notify();
            }
        },
        max_whites:function () {
            $('.hand_overlay_text').text('Waiting for others');
            $(".hand_overlay").show();
        },
        begin_judging:function (topic, cards) {
            $('.play_area_whites').html(ich.t_play_area_judge(cards));
            if (cah.czar == true) {
                notify();
                $('.play_area_overlay').hide();
                $('.hand_overlay_text').text('Judge the white cards!');
                $('.play_area_whites .card_group').one("dblclick",
                    function () {
                        $('.play_area_overlay').show();
                        $('.play_area_overlay_text').text(' ');
                        cah.emit("judge_group", $(this).attr('group_id'));
                    }
                );
            }
            else {
                $('.hand_overlay_text').text('Waiting for the czar');
                $(".hand_overlay").show();
            }
        },
        start_round:function () {
            cah.max_whites = false;
            cah.czar = false;
            $(".hand_overlay").hide();
            $('.play_area_overlay').hide();
            $('.play_area .card').remove();
            $('.play_area .card_group').remove();
            $('.start').hide();
        },
        round_winner:function (topic, data) {
            $('.restart_timer').css('display', 'none');
            if (data.username == cah.username) {
                $('.hand_overlay_text').text('Your cards won!');
            }
            else {
                $('.hand_overlay_text').text(data.username
                    + ' wins this round.');
            }
            $('.card_group[group_id=' + data.group_id + ']')
                .addClass('winning_group')
            $(".hand_overlay").show();
            cah.czar = false;
        },
        winner:function (topic, username) {
            if (username == cah.username) {
                $('.hand_overlay_text').text('[](/trixiesmug)' +
                    ' You win! Was there ever any doubt?');
            }
            else {
                $('.hand_overlay_text').text(username +
                    ' won. They probably cheated. [](/peeved)');
            }
            $(".hand_overlay").show();
        },
        show_timer:function (topic, data) {
            var timer = $(ich.t_timer(data));
            timer.appendTo('.timers');
            var timer_duration = timer.find('.timer_duration');
            var $restart_timer = $('.restart_timer');
            $restart_timer.click(function () {
                cah.emit("restart_timer");
                cah.restarted_timer = true;
            });
            if (cah.czar && !cah.restarted_timer) {
                $restart_timer.css('display', 'inline');
            }

            var interval = setInterval(function () {
                data.duration -= 1;
                timer_duration.text(data.duration);
                if (data.duration <= 0) {
                    clearInterval(interval);
                    timer.remove();
                }
            }, 1000);

            timer.data("interval", interval);
        },
        cancel_timer:function () {
            $('.timer').each(function (i, timer) {
                timer = $(timer);
                var interval = timer.data("interval");
                clearInterval(interval);
                timer.remove();
            });
        },
        sync_me:function (topic, data) {
            if ($('.header input').length > 0) {
                if (data.game_running) {
                    $('.header .start').hide();
                }
                else {
                    $('.header .start').show();
                    $('.card').remove();
                    $('.overlay').hide();
                }
            }
            else {
                $(ich.t_header(data)).appendTo('.header');
                $(".size_slider").slider({
                    range:"max",
                    min:0,
                    max:80,
                    value:0,
                    step:1,
                    slide:function (event, ui) {
                        card_size_css_rule.style.height = (max_card_height - ui.value) + "px";
                        card_size_css_rule.style.width = (max_card_width - ui.value) + "px";
                        card_size_css_rule.style.fontSize = (max_card_font_size - (ui.value /2.5)) + "%";
                        if(ui.value > 50) {
                            card_size_css_rule.style.margin = "2px";
                        }
                    }
                });
            }
        },
        chat_message:function (topic, data) {
            $(ich.t_chat_msg(data)).appendTo('.chat');
            var chat = $('.chat').get(0);
            var scrollHeight = Math.max(chat.scrollHeight, chat.clientHeight);
            chat.scrollTop = scrollHeight - chat.clientHeight;
            var limit = 500;
            while ($(chat).children().length > limit) {
                $(chat).children().first().remove();
            }
        }
    }
})();
