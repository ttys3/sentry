import * as Sentry from '@sentry/react';
import {fireEvent, screen} from '@testing-library/react';

import {mountWithTheme} from 'sentry-test/reactTestingLibrary';

import {LoadingError} from 'sentry/components/loadingError';

describe('LoadingError', () => {
  beforeAll(() => {
    jest.spyOn(console, 'error').mockImplementation(() => void 0);
  });
  it('renders default message', () => {
    mountWithTheme(<LoadingError />);
    expect(screen.getByText('There was an error loading data.')).toBeInTheDocument();
  });
  it('renders custom message', () => {
    mountWithTheme(<LoadingError message="Custom message" />);
    expect(screen.getByText('Custom message')).toBeInTheDocument();
  });
  it('doesnt render retry button', () => {
    mountWithTheme(<LoadingError message="Custom message" />);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
  it('calls onRetry callback', () => {
    const retry = jest.fn();

    mountWithTheme(<LoadingError message="Custom message" onRetry={retry} />);

    fireEvent.click(screen.getByRole('button'));

    expect(retry).toHaveBeenCalledTimes(1);
  });
  it('does not crash in case onRetry throws', () => {
    const sentrySpy = jest.spyOn(Sentry, 'captureException');
    const retry = jest.fn().mockImplementation(() => {
      throw new Error('Failed to retry');
    });

    mountWithTheme(<LoadingError message="Custom message" onRetry={retry} />);

    fireEvent.click(screen.getByRole('button'));

    expect(retry).toHaveBeenCalledTimes(1);
    expect(sentrySpy).toHaveBeenLastCalledWith(new Error('Failed to retry'));
  });
});
