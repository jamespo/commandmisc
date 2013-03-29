package Net::IMAP::Simple::Gmail;
use Text::ParseWords;
use strict;

use vars qw[$VERSION];
$VERSION = (qw$Revision: 0.11 $)[1];

use base qw[Net::IMAP::Simple::SSL];

sub get_labels {
    my ( $self, $number ) = @_;

    my $label;

    return $self->_process_cmd(
        cmd => [ FETCH => qq[$number (X-GM-LABELS)] ],
	final => sub { 
	    my @labels = Text::ParseWords::parse_line(' ', 0, $label);
	    return \@labels },
        process => sub {
            if ( $_[0] =~ /^\* \d+ FETCH \(X-GM-LABELS \((.+)\)\)\s*$/ ) {
                $label = $1;
            }
        },
    );
}


sub add_labels {
    my ( $self, $number, @labels ) = @_;
    return $self->_label_manip( $number, '+X-GM-LABELS', @labels );
}

sub remove_labels {
    my ( $self, $number, @labels ) = @_;
    return $self->_label_manip( $number, '-X-GM-LABELS', @labels );
}


sub _label_manip {
    my ( $self, $number, $op, @labels ) = @_;
    return unless @labels;

    # quote labels with spaces
    @labels = map { / / ? '"' . $_ . '"' : $_ } @labels;
    my $label_line = join ' ', @labels;

    return $self->_process_cmd(
        cmd     => [ STORE => qq[$number $op ($label_line)] ],
        final   => sub { },
        process => sub { },
    );

}

1;

__END__

=head1 NAME

Net::IMAP::Simple::Gmail - Gmail specific support for Net::IMAP::Simple

=head1 SYNOPSIS

  use Net::IMAP::Simple::Gmail;
  my $server = 'imap.gmail.com';
  my $imap = Net::IMAP::Simple::Gmail->new($server);
  
  $imap->login($user => $pass);
  
  my $nm = $imap->select('INBOX');

  for(my $i = 1; $i <= $nm; $i++) {
    # Get labels on message
    my $labels = $imap->get_labels($msg);
  }

=head1 DESCRIPTION

This module is a subclass of L<Net::IMAP::Simple::SSL|Net::IMAP::Simple::SSL> that
includes specific support for Gmail IMAP Extensions. Besides the gmail specific
methods the interface is identical.

=head1 METHODS

=over 4

=item get_labels

my $labels = $imap->get_labels($msgid);

Returns an arrayref of all labels on the message.

=item add_labels

$imap->add_labels($msgid, qw{accounts job});

Adds the labels to the selected message (labels must already exist).

=item remove_labels

$imap->remove_labels($msgid, qw{job});

Removes the labels from the selected message.

=back

=head1 SEE ALSO

L<Net::IMAP::Simple>,
L<perl>.

=head1 AUTHOR

James Powell

=head1 COPYRIGHT

  Copyright (c) 2013 James Powell.  All rights reserved.
  This module is free software; you can redistribute it and/or modify it
  under the same terms as Perl itself.

=cut
